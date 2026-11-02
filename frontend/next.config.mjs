/** @type {import('next').NextConfig} */
const apiBaseUrl = (process.env.API_BASE_URL || "https://aerm-ai.onrender.com").replace(/\/$/, "");

const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiBaseUrl}/api/:path*` }];
  },
};
export default nextConfig;
