"use strict";

$("#users-carousel").owlCarousel({
  items: 4,
  margin: 20,
  autoplay: true,
  autoplayTimeout: 5000,
  loop: true,
  responsive: {
    0: {
      items: 2
    },
    578: {
      items: 4
    },
    768: {
      items: 4
    }
  }
});

 // Follow function
  $('.follow-btn, .following-btn').each(function () {
    var me = $(this),
      follow_text = 'Follow',
      unfollow_text = 'Following';

    me.click(function () {
      if (me.hasClass('following-btn')) {
        me.removeClass('btn-danger');
        me.removeClass('following-btn');
        me.addClass('btn-primary');
        me.html(follow_text);

      } else {
        me.removeClass('btn-primary');
        me.addClass('btn-danger');
        me.addClass('following-btn');
        me.html(unfollow_text);

      }
      return false;
    });
  });
