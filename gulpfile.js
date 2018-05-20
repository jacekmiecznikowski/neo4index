const gulp = require('gulp');
const sass = require('gulp-sass');

gulp.task('sass', function() {
  return gulp.src(['app/static/scss/style.scss'])
    .pipe(sass())
      .pipe(gulp.dest("app/static/css"))
});

gulp.task('js', function() {
  return gulp.src(['node_modules/bootstrap/dist/js/bootstrap.min.js',
  'node_modules/jquery/dist/jquery.min.js', 'node_modules/popper.js/dist/umd/popper.min.js'])
    .pipe(gulp.dest("app/static/js"))
});

gulp.task('serve', ['sass'], function() {
  gulp.watch(['app/static/scss/*.scss'], ['sass']);
});

gulp.task('fonts', function() {
  return gulp.src('node_modules/font-awesome/fonts/*')
    .pipe(gulp.dest("app/static/fonts"));
});
gulp.task('fa', function() {
  return gulp.src('node_modules/font-awesome/css/font-awesome.min.css')
    .pipe(gulp.dest("app/static/css"));
});

gulp.task('default', ['js', 'serve', 'fa', 'fonts']);
