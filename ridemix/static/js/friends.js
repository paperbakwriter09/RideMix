$(function() {
  window.SELECTED_FRIENDS = [];
  window.friend_ajax = $.ajax({
    'url': '/get/friends',
    'datatype': 'text/json',
  }).done(function(data) {
      window.FRIEND_LIST = data;
      var container = $("#friend_add_list").controlgroup("container");
      for(var i in data) {
        addToFriendList(container, i);
      }
        container.trigger('create');
      $.mobile.loading("hide");
    });

  $("#friend_add_select").keyup(function(e) {
    if(window.friend_timer) window.clearTimeout(friend_timer);

    window.friend_timer = window.setTimeout(function() {
      var value = $("#friend_add_select").val();
      var regex = new RegExp(value, "gi");
      var container = $("#friend_add_list").controlgroup("container");
      container.html("");
      for(var i in window.FRIEND_LIST) {
        if(window.FRIEND_LIST[i]['name'].match(regex)) {
          addToFriendList(container, i);
        }
      }
      container.trigger('create');
    }, 2000);
  });

});

function addToSelected(id) {
  var container = $("#selected_list");
  var friend = window.FRIEND_LIST[id];
  var html_id = id + "_selected";
  var div = $("<div>");
  div.attr('id', html_id + "_div");
  var input = $("<input>");
  input.attr('type', 'checkbox');
  input.attr('id', html_id);
  input.attr('data-theme', 'e');
  input.change(function(e) {
    $("#" + e.target.id + "_div").remove();
    var friend_id = parseInt(e.target.id); 
    var friend_div_name = "#" + friend_id + "_friend_div";
    $(friend_div_name).show();
    for(var i = 0; i < window.SELECTED_FRIENDS.length; i++) {
      if(window.SELECTED_FRIENDS[i] == id) {
        window.SELECTED_FRIENDS.splice(i, 1);
        i = window.SELECTED_FRIENDS.length;
      }
    }
    //$("#friend_add_list fieldset").trigger('refresh');
    r.update_results_list();
  });
  var label = $("<label>");
  label.attr('for', html_id);
  label.text(friend['name']);

  div.append(input);
  div.append(label);

  container.append(div);
  container.trigger('create');
  window.SELECTED_FRIENDS.push(id);
  r.update_results_list();
  $("#nofriends").remove();
}

function addToFriendList(container, id) {
  var friend = window.FRIEND_LIST[id];
  var div_id =  id + "_friend";
  var anchor = $("<a>");
  anchor.attr('id', div_id + "_div");
  anchor.attr('data-role', 'button');
  if(window.SELECTED_FRIENDS.indexOf(id) != -1) {
    anchor.css('display', 'none');
  }
  anchor.click(function(e) {
    var this_id = e.currentTarget.id;
    $("#" + this_id).hide();
    var friend_id = parseInt(this_id); 
    addToSelected(friend_id);
    return false;
  });
  anchor.text(friend['name']);
  container.append(anchor);
}

function loadFriends() {
  console.log("Should show load screen now");
  $.mobile.loading("show", {
    text: "Loading Friend List",
    textVisible: true,
    theme: "a",
  });
}
