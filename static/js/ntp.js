/*
NTP.js https://jehiah.cz/a/ntp-for-javascript
copyright Jehiah Czebotar jehiah@gmail.com
licensed under http://unlicense.org/ please modify as needed

to use configure serverUrl to an endpoint that when queried
    GET serverUrl + '?t=' + timestamp_in_miliseconds

returns
    time_offset_in_miliseconds + ':' + argument_t
*/


var NTP = {
  cookieShelfLife : 7, //7 days
  requiredResponses : 2,
  serverTimes : new Array,
  serverUrl : "/getTime",
  resyncTime : 10, // minutes
  sync : function(){
      // if the time was set within the last x minutes; ignore this set request; time was synce recently enough
      var offset = NTP.getCookie("NTPClockOffset");
      if (offset){try{
	  var t = offset.split("|")[1];
	  var d = NTP.fixTime()-parseInt(t,10);
	  if (d < (1000 * 60 * NTP.resyncTime)){return false;} // x minutes; return==skip
      }catch(e){}
      }

      NTP.serverTimes = new Array;
      NTP.getServerTime();
  },
  getNow : function(){
      var date = new Date();
      //return date.getTime();
      return (date.getTime() + (date.getTimezoneOffset() * 60000));
  },
  parseServerResponse : function(data){
    console.log('Response:',data);
     var offset = parseInt(data.offset);
     var origtime = parseInt(data.time);

     console.log('received:',offset);
     console.log('received:',origtime);

     var delay = ((NTP.getNow() - origtime) / 2);
     offset = offset - delay;
     NTP.serverTimes.push(offset);

     // if we have enough responces set cookie
     if (NTP.serverTimes.length >= NTP.requiredResponses){
	 // build average
	 var average = 0;
	 var i=0;
	 for (i=0; i < NTP.serverTimes.length;i++){
	     average += NTP.serverTimes[i];
	 }
	 average = Math.round(average / i);
	 NTP.setCookie("NTPClockOffset",average); // set the new offset
	 NTP.setCookie("NTPClockOffset",average+'|'+NTP.fixTime()); // save the timestamp that we are setting it
     }
     else{
	 NTP.getServerTime();
     }

  },
  getServerTime : function(){

    axios.get(NTP.serverUrl, { params: { t: NTP.getNow()} }).then(
        (response) => {
            var result = response.data;
            console.log(result);
            NTP.parseServerResponse(result);
        },
            (error) => {
            reject(error);
        }
    );

    /*
      try{
	  var req = new Ajax.Request(NTP.serverUrl,{
	      onSuccess : NTP.parseServerResponse,
	      method : "get",
        contentType: "application/json",
	      parameters : "t=" + NTP.getNow()
          });
      }
      catch(e){
	  return false;
	  //prototype.js not available
      }
      */
  },
  setCookie : function(aCookieName,aCookieValue){
    console.log('setCookie called');

     var date = new Date();
     date.setTime(date.getTime() + (NTP.cookieShelfLife * 24*60*60*1000));
     var expires = '; expires=' + date.toGMTString();
     console.log(aCookieName);
     console.log(aCookieValue);

     document.cookie = aCookieName + '=' + aCookieValue + expires + '; path=/';
  },
  getCookie : function(aCookieName){
     var crumbs = document.cookie.split('; ');
     for (var i = 0; i < crumbs.length; i++)
     {
	 var crumb = crumbs[i].split('=');
	 if (crumb[0] == aCookieName && crumb[1] != null)
	 {
	     return crumb[1];
	 }
     }
     return false;
  },
  fixTime : function(timeStamp){
      if(!timeStamp){timeStamp = NTP.getNow();}
      var offset = NTP.getCookie("NTPClockOffset") ;
      try{
	  if (!offset){offset = 0;}else{offset=offset.split("|")[0];}
	  if (isNaN(parseInt(offset,10))){return timeStamp;}
	  return timeStamp + parseInt(offset,10);
      }catch(e){
	  return timeStamp;
      }
  }
}
setTimeout('NTP.sync()',2500);
