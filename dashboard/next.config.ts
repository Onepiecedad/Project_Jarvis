import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
