import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [react()],
	resolve: {
		alias: {
			"@": path.resolve(__dirname, "./src"),
		},
	},
	server: {
		proxy: {
			"/api": {
				target: process.env.NODE_ENV === "development" ? "http://127.0.0.1:5328/api" : "/api/",
				changeOrigin: false,
				rewrite: (path) => path.replace(/^\/api/, ""),
			},
		},
	},
});
