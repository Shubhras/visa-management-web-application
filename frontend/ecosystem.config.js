module.exports = {
    apps: [
   {
      name: "visaManagement",
      script: "npm",
      args: "start",           // Default: development
      watch: true,             // Watches files in development
      env: {
        NODE_ENV: "development",
        PORT: 3000,            // Dev port
      },
      env_production: {
        NODE_ENV: "production",
        PORT: 3000,            // Production port
        // Use "serve -s build" to serve the build folder
        SCRIPT: "npx",
        ARGS: "serve -s build -l 3000"
      },
    },
    ],
  };
  