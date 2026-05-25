/** @type {import('next').NextConfig} */
const nextConfig = {
  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
  
  // Experimental features
  experimental: {
    // Optimize package imports
    optimizePackageImports: ['lucide-react', 'framer-motion', 'recharts'],
  },
  
  // Webpack configuration for better build stability
  webpack: (config, { isServer }) => {
    // Fix for optional dependencies
    config.resolve.fallback = {
      ...config.resolve.fallback,
      fs: false,
      net: false,
      tls: false,
    };
    
    // Optimize for production
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        module: false,
      };
    }
    
    return config;
  },
  
  // Typescript configuration
  typescript: {
    // Ignore build errors for now (fix in separate step)
    ignoreBuildErrors: false,
  },
  
  // ESLint configuration
  eslint: {
    // The project currently validates TypeScript during build; lint runs separately once eslint is installed.
    ignoreDuringBuilds: true,
  },
  
  // Output configuration
  output: 'standalone',
  
  // Image optimization
  images: {
    domains: [],
    unoptimized: true,
  },
  
  // React strict mode
  reactStrictMode: true,
  
  // Compression
  compress: true,
  
  // Production source maps
  productionBrowserSourceMaps: false,
};

module.exports = nextConfig;
