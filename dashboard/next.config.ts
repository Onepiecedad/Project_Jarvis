import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Proxy to Agent Zero to avoid CORS issues
  async rewrites() {
    return [
      {
        source: '/api/jarvis/:path*',
        destination: 'http://localhost:50080/:path*',
      },
    ];
  },
};

export default nextConfig;
