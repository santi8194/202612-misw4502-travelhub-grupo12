module.exports = function (config) {
  config.set({
    frameworks: ['jasmine'],
    plugins: [
      'karma-jasmine',
      'karma-chrome-launcher',
      'karma-coverage',
      'karma-jasmine-html-reporter',
    ],
    browsers: ['ChromeHeadlessNoSandbox'],
    customLaunchers: {
      ChromeHeadlessNoSandbox: {
        base: 'ChromeHeadless',
        flags: [
          '--no-sandbox',
          '--disable-gpu',
          '--disable-dev-shm-usage',
        ],
      },
    },
    coverageReporter: {
      dir: require('path').join(__dirname, './coverage/user-web'),
      subdir: '.',
      reporters: [{ type: 'html' }, { type: 'text' }],
    },
    reporters: ['progress', 'kjhtml'],
    restartOnFileChange: true,
  });
};