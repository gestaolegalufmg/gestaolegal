"use strict";

$("#swal-1").click(function() {
	swal('Your Profile is changed successfully.');
});

$("#swal-2").click(function() {
	swal('Profile', 'Your Profile is changed successfully.', 'success');
});

$("#swal-3").click(function() {
	swal('Profile', 'You should change your profile picture.', 'warning');
});

$("#swal-4").click(function() {
	swal('Profile', 'you can check your information in your profile.', 'info');
});

$("#swal-5").click(function() {
	swal('Profile', 'some mistake is there.', 'error');
});

$("#swal-6").click(function() {
  swal({
      title: 'Are you sure?',
      text: 'Once deleted, you will not be able to recover this file!',
      icon: 'warning',
      buttons: true,
      dangerMode: true,
    })
    .then((willDelete) => {
      if (willDelete) {
      swal('Your file has been deleted!', {
        icon: 'success',
      });
      } else {
      swal('Your file is safe!');
      }
    });
});

$("#swal-7").click(function() {
  swal({
    title: 'please fill your name?',
    content: {
    element: 'input',
    attributes: {
      placeholder: 'Your name',
      type: 'text',
    },
    },
  }).then((data) => {
    swal('Hello, ' + data + '!');
  });
});

$("#swal-8").click(function() {
  swal('This modal will be hide soon!', {
    buttons: false,
    timer: 3000,
  });
});