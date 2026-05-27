import { NextRequest, NextResponse } from 'next/server';

const publicRoutes = new Set(['/', '/landing', '/login', '/sign-in', '/signup', '/sign-up']);

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('access_token')?.value;

  if (publicRoutes.has(pathname) && token && ['/login', '/sign-in', '/signup', '/sign-up'].includes(pathname)) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  if (!token && !publicRoutes.has(pathname)) {
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('next', pathname);
    return NextResponse.redirect(loginUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
};
