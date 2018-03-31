$('#search-button').click(function(){
	$('#navbar form.search').toggleClass('hidden-xs');
});
$('li.notification,li.profile,#th-list').click(function(){
	$('#navbar form.search').addClass('hidden-xs');
});

$('#th-list').click(function(){
	$('#mobile-bar').toggleClass('hidden');
});
$('#search-button,li.notification,li.profile').click(function(){
	$('#mobile-bar').addClass('hidden');
});
$('#mobile-bar li.dropbar').click(function(){
  $('#mobile-bar li.dropbar ul').toggleClass('hidden');
});

$('.ajax').submit(function(event){
	var $this = $(this);
  var message = $( this ).prev();
  	event.preventDefault();
  	$.ajax({
  		type:"POST",
  		url :$this.attr('action'),
  		data :$this.serialize(),
  		success: function(data){
  			if(data['status']=='true'){
  				message.removeClass('alert-danger fade in');
  				message.addClass('alert-success fade in');
	  			message.html('<strong>Success! </strong>' + data['message']);
	  			$this[0].reset();
	  			message.removeClass('hide').delay(1000).queue(function(){
				    $(this).addClass("hide").dequeue();
				});
  			}else if(data['status']=='false'){
  				message.removeClass('alert-success fade in');
  				message.addClass('alert-danger fade in');
  				message.html( '<strong>Error! </strong>' + data['message']);
  				message.removeClass('hide');
  			}
  		},
      error: function(data){
          message.removeClass('alert-success fade in');
          message.addClass('alert-danger fade in');
          message.html( '<strong>Error! </strong>' + 'Something went wrong ');
          message.removeClass('hide');
      },
  		dataType:"json",
  	});
});
