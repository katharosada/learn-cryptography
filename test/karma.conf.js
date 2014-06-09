module.exports = function(config){
  config.set({

    basePath : '../',

    files : [
      'learn-cryptography/client/bower_components/angular/angular.js',
      'learn-cryptography/client/bower_components/angular-route/angular-route.js',
      'learn-cryptography/client/bower_components/angular-mocks/angular-mocks.js',
      'learn-cryptography/client/js/**/*.js',
      'test/unit/**/*.js'
    ],

    autoWatch : true,

    frameworks: ['jasmine'],

    browsers : ['Chrome'],

    plugins : [
            'karma-chrome-launcher',
            'karma-firefox-launcher',
            'karma-jasmine',
            'karma-junit-reporter'
            ],

    junitReporter : {
      outputFile: 'test_out/unit.xml',
      suite: 'unit'
    }

  });
};
