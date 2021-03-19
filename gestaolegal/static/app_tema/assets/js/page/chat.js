"use strict";

$.chatCtrl = function(element, chat) {
    var chat = $.extend({
      position: 'chat-right',
      text: '',
      time: moment(new Date().toISOString()).format('hh:mm'),
      picture: '',
      type: 'text', // or typing
      timeout: 0,
      onShow: function() {}
    }, chat);

    var target = $(element),
        element = '<div class="chat-item '+chat.position+'" style="display:none">' +
                  '<img src="'+chat.picture+'">' +
                  '<div class="chat-details">' +
                  '<div class="chat-text">'+chat.text+'</div>' +
                  '<div class="chat-time">'+chat.time+'</div>' +
                  '</div>' +
                  '</div>',
        typing_element = '<div class="chat-item chat-left chat-typing" style="display:none">' +
                  '<img src="'+chat.picture+'">' +
                  '<div class="chat-details">' +
                  '<div class="chat-text"></div>' +
                  '</div>' +
                  '</div>';

      var append_element = element;
      if(chat.type == 'typing') {
        append_element = typing_element;
      }

      if(chat.timeout > 0) {
        setTimeout(function() {
          target.find('.chat-content').append($(append_element).fadeIn());
        }, chat.timeout);
      }else{
        target.find('.chat-content').append($(append_element).fadeIn());
      }

      var target_height = 0;
      target.find('.chat-content .chat-item').each(function() {
        target_height += $(this).outerHeight();
      });
      setTimeout(function() {
        target.find('.chat-content').scrollTop(target_height, -1);
      }, 100);
      chat.onShow.call(this, append_element);
  }

  if ($("#chat-scroll").length) {
    $("#chat-scroll").css({
      height: 450
    }).niceScroll();
  }
  
    if ($(".chat-content").length) {
    $(".chat-content").niceScroll({
      cursoropacitymin: .3,
      cursoropacitymax: .8,
    });
    $('.chat-content').getNiceScroll(0).doScrollTop($('.chat-content').height());
  }
var chats = [
  {
    text: 'Hello, How are you ?!',
    position: 'left'
  },
  {
    text: 'I am Fine',
    position: 'right'
  },
  {
    text: 'Whats about you?',
    position: 'right'
  },
  {
    text: 'I am fine too!!',
    position: 'left'
  },
  {
    text: 'Could you please check your task?',
    position: 'left'
  },
  {
    text: 'Yes I am.',
    position: 'right'
  },
  {
    text: 'Do you have any questions?',
    position: 'left'
  },
  {
    text: 'No.',
    position: 'right'
  },
  {
	    text: 'That is great.',
	    position: 'left'
  },
  {
	    text: 'if you will have any questions,then let me know..',
	    position: 'left'
  },
  {
    text: 'Delevered me when complete',
    position: 'left'
  },
  {
    text: 'Okay Sure.',
    position: 'right'
  },
  {
    text: 'Thank You...',
    position: 'left'
  },
  {
    typing: true,
    position: 'left'
  }
];
for(var i = 0; i < chats.length; i++) {
  var type = 'text';
  if(chats[i].typing != undefined) type = 'typing';
  $.chatCtrl('#mychatbox', {
    text: (chats[i].text != undefined ? chats[i].text : ''),
    picture: (chats[i].position == 'left' ? 'assets/img/users/user-6.png' : 'assets/img/users/user-1.png'),
    position: 'chat-'+chats[i].position,
    type: type
  });
}

$("#chat-form").submit(function() {
  var me = $(this);

  if(me.find('input').val().trim().length > 0) {      
    $.chatCtrl('#mychatbox', {
      text: me.find('input').val(),
      picture: 'assets/img/users/user-5.png',
    });
    me.find('input').val('');
  } 
  return false;
});


