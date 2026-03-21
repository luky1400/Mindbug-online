import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            "/game": "http://127.0.0.1:8000",
            "/card-images": "http://127.0.0.1:8000",
            "/socket.io": {
                target: "http://127.0.0.1:8000",
                ws: true
            }
        }
    }
});
