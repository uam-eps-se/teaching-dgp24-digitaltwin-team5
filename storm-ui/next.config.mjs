/** @type {import('next').NextConfig} */
const nextConfig = {
  basePath: process.env.BASEPATH,
  async redirects() {
    return [
      {
        source: "/",
        destination: "/rooms",
        permanent: true,
      },
    ];
  },
  eslint: {
    ignoreDuringBuilds: true
  }
};

export default nextConfig
