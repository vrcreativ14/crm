var gulp         = require('gulp');
var sass         = require('gulp-sass')(require('sass'));
var concat       = require('gulp-concat');
var browsersync  = require('browser-sync').create();
var webserver    = require('gulp-webserver');
var minify       = require('gulp-minifier');
var minifyCSS    = require('gulp-minify-css');
var autoprefixer = require('gulp-autoprefixer');
var uglify       = require('gulp-uglify');
var print        = require('gulp-print').default;
var debug        = require('gulp-debug');


var paths_for_css_files = [
  '../../common_static/css/*.css',
  '../../common_static/libs/**/*.css',
  '../../common_static/libs/**/css/*.css'
];

var paths_for_js_files = [
  '../../common_static/libs/*.js',
  '../../common_static/libs/**/*.js',
];

var paths_for_public_css_files = [
  '!../../common_static/public/css/override/*.css',
  '../../common_static/public/css/*.css',
  '../../common_static/public/css/**/*.css',
  '../../common_static/public/libs/*.css',
  '../../common_static/public/libs/**/*.css',
];

var paths_for_public_js_files = [
  '../../common_static/public/js/*.js',
  '../../common_static/public/libs/**/*.js'
];

var path_for_sass_files = '../../common_static/scss/*.scss';
var path_for_public_sass_files = [
  '../../common_static/public/scss/*.scss',
  '../../common_static/public/scss/**/*.scss',
];
var path_for_distribution = '../../common_static/dist';

// Override CSS files
var path_for_overrided_sass_files = '../../common_static/public/scss/override/*.scss';

// Custom JS for each page
var path_for_custom_js_files = [
  '../../common_static/js/components/*.js',
  '../../common_static/js/components/mortgage/*.js',

];

gulp.task('minifycss', async function() {
  var file_name = "style.min.css";

  if (process.argv[3] == '-p') {
    return gulp.src(paths_for_css_files)
      .pipe(minifyCSS())
      .pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9'))
      .pipe(concat(file_name))
      .pipe(gulp.dest(path_for_distribution));
  } else {
    return gulp.src(paths_for_css_files)
      .pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9'))
      .pipe(concat(file_name))
      .pipe(gulp.dest(path_for_distribution))
      .pipe(browsersync.reload({
        stream: true
      }));
  }
});

gulp.task('minifycss_public', async function() {
  var file_name = "style.public.min.css";
  if (process.argv[3] == '-p') {
    return gulp.src(paths_for_public_css_files)
      .pipe(minifyCSS())
      .pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9'))
      .pipe(concat(file_name))
      .pipe(gulp.dest(path_for_distribution));
  } else {
    return gulp.src(paths_for_public_css_files)
      .pipe(autoprefixer('last 2 version', 'safari 5', 'ie 8', 'ie 9'))
      .pipe(concat(file_name))
      .pipe(gulp.dest(path_for_distribution))
      .pipe(browsersync.reload({
        stream: true
      }));
  }
});

gulp.task('minifyjs', async function() {
  var file_name = "scripts.min.js";

  if (process.argv[3] == '-p') {
    gulp.src(paths_for_js_files).pipe(concat(file_name)).pipe(uglify()).pipe(gulp.dest(path_for_distribution));
  } else {
    gulp.src(paths_for_js_files).pipe(concat(file_name)).pipe(gulp.dest(path_for_distribution)).pipe(browsersync.reload({
      stream: true
    }));
  }
});

gulp.task('minifycustomjs', async function() {
  var file_name = "app.js";

  if (process.argv[3] == '-p') {
    gulp.src(path_for_custom_js_files).pipe(concat(file_name)).pipe(uglify()).pipe(gulp.dest(path_for_distribution));
  } else {
    gulp.src(path_for_custom_js_files).pipe(concat(file_name)).pipe(gulp.dest(path_for_distribution)).pipe(browsersync.reload({
      stream: true
    }));
  }
});

gulp.task('minifyjs_public', async function() {
  var file_name = "scripts.public.min.js";

  if (process.argv[3] == '-p') {
    gulp.src(paths_for_public_js_files).pipe(concat(file_name)).pipe(uglify()).pipe(gulp.dest(path_for_distribution));
  } else {
    gulp.src(paths_for_public_js_files).pipe(concat(file_name)).pipe(gulp.dest(path_for_distribution)).pipe(browsersync.reload({
      stream: true
    }));
  }
});

// Compile SASS to CSS
gulp.task('sass', gulp.series('minifycss', function(){
  return gulp.src(path_for_sass_files)
    .pipe(sass()) // Using gulp-sass
    .pipe(gulp.dest('../../common_static/css'));
}));

gulp.task('sass_public', gulp.series('minifycss_public', function() {
  return gulp.src(path_for_public_sass_files)
    // .pipe(debug({title: 'before:'}))
    .pipe(sass()) // Using gulp-sass
    // .pipe(debug({title: 'after:'}))
    .pipe(gulp.dest('../../common_static/public/css'))
    .pipe(print());
}));

gulp.task('sass_public_override', async function() {
  return gulp.src(path_for_public_sass_files)
    .pipe(sass()) // Using gulp-sass
    .pipe(gulp.dest('../../common_static/public/css'))
    .pipe(print());
});

gulp.task('browsersync', async function() {
  browsersync.init({
    proxy: "localhost:8002",
  });
});

// Watch JS/Sass files
gulp.task('watch', function(done) {
  gulp.watch(path_for_sass_files, gulp.series('sass'));
  gulp.watch(path_for_public_sass_files, gulp.series('sass_public'));
  gulp.watch(path_for_overrided_sass_files, gulp.series('sass_public_override'));
  gulp.watch(paths_for_js_files, gulp.series('minifyjs'));
  gulp.watch(path_for_custom_js_files, gulp.series('minifycustomjs'));
  gulp.watch(paths_for_public_js_files, gulp.series('minifyjs_public'));
  done();
});

gulp.task('webserver', async function() {
  gulp.src('app')
    .pipe(webserver({
      livereload: true,
      directoryListing: true,
      open: true
    }));
});

gulp.task('build', gulp.series('minifycss', 'minifycss_public', 'minifyjs', 'minifycustomjs', 'minifyjs_public'));
gulp.task('default', gulp.series('sass', 'sass_public', 'sass_public_override', 'build', 'browsersync', 'watch'));

gulp.task('crm', gulp.series('sass', 'sass_public', 'build', 'browsersync', 'watch'));
