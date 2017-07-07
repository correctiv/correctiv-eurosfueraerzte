var gulp = require('gulp');
var less = require('gulp-less');
var autoprefixer = require('gulp-autoprefixer');
var watch = require('gulp-watch');
var livereload = require('gulp-livereload');
var exec = require('child_process').exec;
var combiner = require('stream-combiner2');
var browserify = require('browserify');
var babelify = require('babelify');
var uglify = require('gulp-uglify');
var buffer = require('vinyl-buffer');
var source = require('vinyl-source-stream');

var JS_SOURCE = 'correctiv_eurosfueraerzte/static/eurosfueraerzte/js/';
var JS_DEST = 'correctiv_eurosfueraerzte/static/eurosfueraerzte/dist/';
var MAIN_JS_FILE = 'map.js';

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

/* Transpile, browsify and uglify/minify ES6 */
gulp.task('babel', function () {
  var bundler = browserify(JS_SOURCE + MAIN_JS_FILE, {
    standalone: 'eurosfueraerzte'
  });

  bundler.transform(babelify);
  bundler.bundle()
    .on('error', function (err) { console.error(err); })
    .pipe(source(MAIN_JS_FILE))
    .pipe(buffer())
    .pipe(uglify())
    .pipe(gulp.dest(JS_DEST));
});

/* Watch files For changes */
gulp.task('watch', function() {
  livereload.listen();
  gulp.watch(CSS_SOURCE + '/**/*.less', ['less']);
  // calls "build-js" whenever anything changes
  gulp.watch('correctiv_eurosfueraerzte/static/eurosfueraerzte/js/**/*.js', ["babel"]);

  /* Trigger a live reload on any Django template changes */
  gulp.watch('**/templates/**').on('change', livereload.changed);

  /* Trigger a live reload upon CSS complilation */
  gulp.watch(CSS_DEST + '/**').on('change', livereload.changed);

  /* Trigger a live reload upon JS complilation */
  gulp.watch(JS_DEST + '/**').on('change', livereload.changed);
});

/* Watch and rebundle code during development */
gulp.task('dev', ['babel', 'less', 'watch']);

/* Create a build of frontend code */
gulp.task('default', ['babel', 'less']);
