import { NextRequest, NextResponse } from 'next/server';

const publicRoutes = new Set(['/', '/landing', '/login', '/sign-in', '/signup', '/sign-up']);

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('access_token')?.value;
  const refreshToken = request.cookies.get('refresh_token')?.value;

  const tokenExpired = token ? isJwtExpired(token) : true;
  const refreshTokenExpired = refreshToken ? isJwtExpired(refreshToken) : true;

  const isPublicRoute = publicRoutes.has(pathname);

  if (!isPublicRoute) {
    if (tokenExpired && refreshTokenExpired) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('next', pathname);
      const response = NextResponse.redirect(loginUrl);
      response.cookies.delete('access_token');
      response.cookies.delete('refresh_token');
      return response;
    }
  }

  if (['/login', '/sign-in', '/signup', '/sign-up'].includes(pathname)) {
    if (!tokenExpired || !refreshTokenExpired) {
      return NextResponse.redirect(new URL('/dashboard', request.url));
    }
  }

  return NextResponse.next();
}

function isJwtExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1] ?? ''));
    return Boolean(payload.exp && payload.exp * 1000 <= Date.now());
  } catch {
    return true;
  }
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)']
};
