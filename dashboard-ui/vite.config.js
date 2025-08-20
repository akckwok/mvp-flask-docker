const { resolve } = require('path')

module.exports = {
  root: '.',
  build: {
    outDir: 'dist',
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        login: resolve(__dirname, 'login.html'),
        register: resolve(__dirname, 'register.html'),
        directory: resolve(__dirname, 'directory.html'),
        profile: resolve(__dirname, 'profile.html'),
        profile_creation: resolve(__dirname, 'profile_creation.html'),
        project_submission: resolve(__dirname, 'project_submission.html'),
        data_submission: resolve(__dirname, 'data_submission.html'),
      },
    },
  },
}
