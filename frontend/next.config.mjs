/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    serverActions: false
  },
  eslint: {
    ignoreDuringBuilds: true
  },
  typescript: {
    ignoreBuildErrors: false
  }
};

export default nextConfig;
