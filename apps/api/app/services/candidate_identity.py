import re
from dataclasses import dataclass


EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")
PHONE_RE = re.compile(r"(?:\+?\d[\s().-]?){8,}\d")
NAME_RE = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}$")


@dataclass(frozen=True)
class CandidateIdentity:
    full_name: str
    email: str | None
    phone: str | None
    source: str


class CandidateIdentityExtractor:
    """Conservative resume identity extraction with deterministic fallbacks."""

    blocked_headers = {
        "resume",
        "curriculum vitae",
        "cv",
        "profile",
        "candidate profile",
        "summary",
        "experience",
        "education",
        "skills",
        "projects",
        "contact",
        "professional experience",
        "work experience",
    }

    def extract(
        self,
        text: str,
        filename: str | None = None,
        metadata: dict | None = None,
    ) -> CandidateIdentity:
        metadata = metadata or {}
        cleaned_lines = [line.strip() for line in text.splitlines() if line.strip()]
        header_lines = cleaned_lines[:12]
        email = self._email(text)
        phone = self._phone(text)

        for line in header_lines[:8]:
            candidate = self._clean_name(line)
            if candidate:
                return CandidateIdentity(candidate, email, phone, "resume_header")

        ner_name = self._ner_like_name(header_lines)
        if ner_name:
            return CandidateIdentity(ner_name, email, phone, "ner_like_header")

        if email:
            email_name = self._name_from_username(email.split("@", 1)[0])
            if email_name:
                return CandidateIdentity(email_name, email, phone, "email_username")

        filename_name = self._name_from_filename(filename)
        if filename_name:
            return CandidateIdentity(filename_name, email, phone, "filename")

        metadata_name = self._name_from_metadata(metadata)
        if metadata_name:
            return CandidateIdentity(metadata_name, email, phone, "pdf_metadata")

        regex_name = self._regex_name(text)
        if regex_name:
            return CandidateIdentity(regex_name, email, phone, "regex")

        for line in cleaned_lines[:20]:
            candidate = self._clean_name(line)
            if candidate:
                return CandidateIdentity(candidate, email, phone, "top_document_lines")

        return CandidateIdentity("Candidate Profile", email, phone, "fallback")

    @staticmethod
    def _email(text: str) -> str | None:
        match = EMAIL_RE.search(text)
        return match.group(0).lower() if match else None

    @staticmethod
    def _phone(text: str) -> str | None:
        match = PHONE_RE.search(text)
        return re.sub(r"\s+", " ", match.group(0)).strip() if match else None

    def _clean_name(self, value: str) -> str | None:
        for segment in re.split(r"[\|,;:]+", value):
            segment = re.sub(r"\s+", " ", segment).strip()
            if segment and segment != value:
                candidate = self._clean_name(segment)
                if candidate:
                    return candidate
        value = re.sub(r"[\|,;:]+", " ", value)
        value = re.sub(r"\s+", " ", value).strip()
        if not value or value.lower() in self.blocked_headers:
            return None
        if "@" in value or any(char.isdigit() for char in value):
            return None
        words = value.split()
        if len(words) > 4 or len(value) > 80:
            return None
        if any(word.lower() in {"engineer", "developer", "manager", "analyst", "consultant"} for word in words):
            return None
        if NAME_RE.match(value):
            return value
        titled = " ".join(part.capitalize() for part in re.findall(r"[A-Za-z]+", value))
        if NAME_RE.match(titled):
            return titled
        return None

    def _regex_name(self, text: str) -> str | None:
        patterns = [
            r"(?:name|candidate)\s*[:\-]\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})",
            r"^([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})\s*$",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.MULTILINE)
            if match:
                cleaned = self._clean_name(match.group(1))
                if cleaned:
                    return cleaned
        return None

    def _ner_like_name(self, lines: list[str]) -> str | None:
        for line in lines[:6]:
            compact = re.sub(r"\s+", " ", line).strip()
            if compact.isupper() and 2 <= len(compact.split()) <= 4:
                candidate = self._clean_name(compact.title())
                if candidate:
                    return candidate
            label_match = re.search(r"(?:^|\b)(?:name|candidate)\s*[:\-]\s*(.+)$", compact, flags=re.IGNORECASE)
            if label_match:
                candidate = self._clean_name(label_match.group(1))
                if candidate:
                    return candidate
        return None

    def _name_from_username(self, username: str) -> str | None:
        parts = [part for part in re.split(r"[._\-+]+", username) if part and not part.isdigit()]
        if len(parts) < 2:
            return None
        return self._clean_name(" ".join(parts[:4]))

    def _name_from_filename(self, filename: str | None) -> str | None:
        if not filename:
            return None
        stem = re.sub(r"\.[A-Za-z0-9]+$", "", filename)
        stem = re.sub(r"(?i)\b(resume|cv|profile|latest|final|updated)\b", " ", stem)
        return self._name_from_username(stem.replace(" ", "_"))

    def _name_from_metadata(self, metadata: dict) -> str | None:
        for key in ["author", "Author", "creator", "Creator", "title", "Title"]:
            candidate = self._clean_name(str(metadata.get(key) or "").strip())
            if candidate:
                return candidate
        return None
