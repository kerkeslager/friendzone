(function(fn) {
  if (document.readyState !== 'loading') {
    fn();
  } else {
    document.addEventListener('DOMContentLoaded', fn);
  }
})(function() {
  /* This code will be called on document ready. */
  console.log('This user has JavaScript enabled!');
});

