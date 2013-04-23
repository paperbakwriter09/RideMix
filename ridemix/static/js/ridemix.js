/*
 This function represents the RideMix application in Javascript
 controlling the function of all parts of the application, which
 currently include the map, the search results, and the friends page
 */
function RideMix(map_div_id, results_div_id, friends_div_id) {
    this.map = null;				// - Google Maps map
    this.cur_loc_marker = null;		// - Google Maps marker for user's position
    this.search_results = null;		// - list of dics that represent search results
    								//   must be sorted by user
    this.types = 'restaurant';		// - TODO let user select eventually...
    this.map_div_id = map_div_id;
    this.results_div_id = results_div_id;
    //this.friends_div_id = friends_div_id;	// - I'm not touching friends right now,
    									 	//   Mike you can do that
}

RideMix.prototype.init = function() {
	console.log("init called");
	$("#map_button").click(function(e) {
        $("#navbar .cell").removeClass('selected');
        $(e.target).addClass('selected');
        $("#map_canvas").show();
        $("#location_list").hide();
        $("#friend_list").hide();
    });
    $("#map_button").click()

    $("#list_button").click(function(e) {
        $("#navbar .cell").removeClass('selected');
        $(e.target).addClass('selected');
        $("#map_canvas").hide();
        $("#friend_list").hide();
        $("#location_list").show();
    });

    $("#friend_button").click(function(e) {
        $("#navbar .cell").removeClass('selected');
        $(e.target).addClass('selected');
        $("#map_canvas").hide();
        $("#location_list").hide();
        $("#friend_list").show();
    });

    this.initialize_map();
	//TODO window.watchID = navigator.geolocation.watchPosition(this.watch_pos_callback);
}

RideMix.prototype.watch_pos_callback = function(location) {
	console.log(location);
    var pos = new google.maps.LatLng(location.coords.latitude, location.coords.longitude);
    this.cur_loc_marker.setPosition(pos);
    this.map.setCenter(marker.position);
    //TODO this.search_results = get search results
}

RideMix.prototype.initialize_map = function() {
	console.log("initialize_map called");
	var mapOptions = {
        zoom: 16,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    this.map = new google.maps.Map(document.getElementById(this.map_div_id),
         mapOptions);
    if(navigator.geolocation) {
    	var obj = this;
        navigator.geolocation.getCurrentPosition(function(position) {
        	obj.get_pos_callback(position);
        }, function() {
        	// Geolocation Error
            obj.handle_no_geolocation(true);
        });
    } else {
        // Browser doesn't support Geolocation
        this.handle_no_geolocation(false);
    }
}

RideMix.prototype.get_pos_callback = function(position) {
	console.log("get_pos_callback called");
	var pos = new google.maps.LatLng(position.coords.latitude,
                                             position.coords.longitude);
    var image = 'http://static.ridemix.com/prod/media/minibug.jpg';
    this.cur_loc_marker = new google.maps.Marker({
        map: this.map,
        position: pos,
        animation: google.maps.Animation.DROP,
        title: 'You are here!',
        icon: image
    });

    this.map.setCenter(pos);
    this.update_results_list();
}

RideMix.prototype.handle_no_geolocation = function(error_flag) {
	if (errorFlag) {
        var content = 'Error: The Geolocation service failed.';
    } else {
    	var content = 'Error: Your browser doesn\'t support geolocation.';
    }

    var options = {
        map: this.map,
        position: new google.maps.LatLng(60, 105),
        content: content
    };

    var infowindow = new google.maps.InfoWindow(options);
    this.map.setCenter(options.position);
}

RideMix.prototype.update_results_list = function() {
	console.log("update_results_list called");
	var url = 'get/rankings?location=';
    var latitude = this.cur_loc_marker.position.lat();
    var longitude = this.cur_loc_marker.position.lng();
    var ll_string = latitude + "," + longitude;
    url += ll_string;
    url += '&types=' + this.types;
    console.log(url);
    
    var obj = this;
    $.getJSON(url, function(json_data) {
    	obj.search_results = json_data;
        obj.calc_latlng_dists();
        //obj.combine_results(); // should be obj.sort results
        //obj.write_places_results_list();
    });
}

RideMix.prototype.calc_latlng_dists = function() {
	console.log("calc_latlng_dists called");

    // sliced in backend now

	var destinations = new Array();
	for (i=0; i < r.search_results.length; i++) {
		destinations.push(new google.maps.LatLng(this.search_results[i].lat, this.search_results[i].lng));
	}
    console.log(destinations);

	var service = new google.maps.DistanceMatrixService();

	var obj = this;
    service.getDistanceMatrix({
        origins: [this.cur_loc_marker.position],
        destinations: destinations,
        travelMode: google.maps.TravelMode.DRIVING,	//TODO user choice
        unitSystem: google.maps.UnitSystem.IMPERIAL	//TODO user choice
    }, function(response, status) { obj.dist_callback(response, status); });
}

RideMix.prototype.dist_callback = function(response, status) {
	console.log("dist_callback called");
	if (status == google.maps.DistanceMatrixStatus.OK) {
    	for (var i = 0; i < response.originAddresses.length; i++) {
      		var results = response.rows[i].elements;
      		for (var j = 0; j < results.length; j++) {
        		var distance = results[j].distance.text;
        		this.search_results[j]["distance"] = distance;
      		}
    	}
    	var obj = this;
    	this.search_results.sort(function(a,b) {
    		return obj.ridemix_compare(a,b);
    	});
    	this.write_search_results()
	} else {
		console.log(status);
	}
}

RideMix.prototype.write_search_results = function() {
	console.log("write_search_results called");
    //var result_string = "<li data-role=\"list-divider\" role=\"heading\">Combined Results</li>";
    //var result_string = "<div data-role=\"collapsible\">";
    var result_string = "";  
    //result_string += "<h3>Combined Results</h3></div>";
    for (i=0;i<this.search_results.length;i++) {
        var randNumber = Math.floor(Math.random()*6);
        var rand2 = Math.floor(Math.random()*21);
        place = this.search_results[i];
        console.log(place);

        result_string += "<div data-role=\"collapsible\">";
        result_string += "<h3>" + place.name + " (" + place.distance + ")</h3>";
        result_string += "<p><a href=\"http://maps.google.com?q=stanford\">Link</a>";
        if(place.gp_rating)
          result_string += "<br />Google Rating: " + place.gp_rating;
        if(place.phone)
          result_string += "<br /><a href=\"tel://" + place.phone + "\">Phone</a>";
        result_string += "</p></div>";

        //Begin random friend stats 
        /*if (randNumber == 2)
          result_string += "<div class=\"friends_insert\">" + rand2 + " of your friends like this!</div>";
        else if (randNumber == 3) {
          var selected_size = window.SELECTED_FRIENDS.length;
          if (selected_size != 0) {
            var rand_friend = Math.floor(Math.random()*selected_size);
             var friend_name = window.FRIEND_LIST[rand_friend]['name']
             result_string += "<div class=\"friend_insert\">" + friend_name + " likes this!</div>";
         }
          
        }
        */
        //End random friend stats
        
        /*if (place.open_now) {
            result_string += "<div style=\"float:right;\">" + place.open_now + "</div><br />";
        } else {
            open_now = place.is_closed ? "Closed" : "Open";
            result_string += "<div style=\"float:right;\">" + open_now + "</div><br />";
        }*/
    }
    $("#"+this.results_div_id).html(result_string).collapsibleset();
}

RideMix.prototype.ridemix_compare = function(a,b) {
	// ideas: slider to make distance more important
	// track how user values distance over rating and friends
	
	// what contributes to rating:
	// 1. distance, 2.5 miles per star
	// 2. gp_rating
	
	a_score = 0; // higher score is better
	b_score = 0;
	
	a_dist = parseFloat(a.distance);
    b_dist = parseFloat(b.distance);
    
    if (a.distance.search("ft") != -1) {
    	a_dist *= 0.000189393939; // Google calculator, 1 ft = 0.000189393939 mi
    }
    if (b.distance.search("ft") != -1) {
    	b_dist *= 0.000189393939;
    }
    
    a_score += (-2.5 * a_dist);
    b_score += (-2.5 * b_dist);
    
    if (a.gp_rating) {
    	a_score += a.gp_rating;
    }
	if (b.gp_rating) {
		b_score += b.gp_rating;
	}

    if (a_score > b_score) { return -1; }
    else if (a_score < b_score) { return 1; }
	else { return 0; }
}

$(function() {
  r = new RideMix('map_canvas','places_list','');
  r.init();

  $("#location_page").on('pagebeforeshow', function(e) {
    r.write_search_results();
  });
});
