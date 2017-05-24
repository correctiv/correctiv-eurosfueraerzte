var gulp = require('gulp');
var less = require('gulp-less');
var autoprefixer = require('gulp-autoprefixer');
var watch = require('gulp-watch');
var livereload = require('gulp-livereload');
var exec = require('child_process').exec;
var combiner = require('stream-combiner2');
var babel = require('gulp-babel');
var uglify = require('gulp-uglify');

var CSS_SOURCE = 'correctiv_eurosfueraerzte/static/eurosfueraerzte/less';
var CSS_DEST = 'correctiv_eurosfueraerzte/static/eurosfueraerzte/css';
var MAIN_LESS_FILE = '/eurosfueraerzte.less';

/* Compile, minify, and compress LESS files */
gulp.task('less', function() {
  var combined = combiner.obj([
    gulp.src(CSS_SOURCE + MAIN_LESS_FILE),
    less(),
    autoprefixer({
      browsers: ['last 2 versions'],
      cascade: false
    }),
    gulp.dest(CSS_DEST)
  ]);

  // any errors in the above streams will get caught
  // by this listener, instead of being thrown:
  combined.on('error', console.error.bind(console));

  return combined;
});

/* Watch files For changes */
gulp.task('watch', function() {
  livereload.listen();
  gulp.watch(CSS_SOURCE + '/**/*.less', ['less']);


  /* Trigger a live reload on any Django template changes */
  gulp.watch('**/templates/**').on('change', livereload.changed);

  /* Trigger a live reload upon CSS complilation */
  gulp.watch(CSS_DEST + '/**').on('change', livereload.changed);
});

/* Watch and rebundle code during development */
gulp.task('dev', ['less', 'watch']);

/* Create a build of frontend code */
gulp.task('default', ['less']);
