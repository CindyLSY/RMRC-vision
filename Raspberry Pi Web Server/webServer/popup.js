// Copyright (c) 2014 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

var port;

/**
 * Get the current URL.
 *
 * @param {function(string)} callback called when the URL of the current tab
 *   is found.
 */
function getCurrentTabUrl(callback) {
  // Query filter to be passed to chrome.tabs.query - see
  // https://developer.chrome.com/extensions/tabs#method-query
  var queryInfo = {
    active: true,
    currentWindow: true
  };

  chrome.tabs.query(queryInfo, (tabs) => {
    // chrome.tabs.query invokes the callback with a list of tabs that match the
    // query. When the popup is opened, there is certainly a window and at least
    // one tab, so we can safely assume that |tabs| is a non-empty array.
    // A window can only have one active tab at a time, so the array consists of
    // exactly one tab.
    var tab = tabs[0];

    // A tab is a plain object that provides information about the tab.
    // See https://developer.chrome.com/extensions/tabs#type-Tab
    var url = tab.url;

    // tab.url is only available if the "activeTab" permission is declared.
    // If you want to see the URL of other tabs (e.g. after removing active:true
    // from |queryInfo|), then the "tabs" permission is required to see their
    // "url" properties.
    console.assert(typeof url == 'string', 'tab.url should be a string');

    callback(url);
  });

  // Most methods of the Chrome extension APIs are asynchronous. This means that
  // you CANNOT do something like this:
  //
  // var url;
  // chrome.tabs.query(queryInfo, (tabs) => {
  //   url = tabs[0].url;
  // });
  // alert(url); // Shows "undefined", because chrome.tabs.query is async.
}

/**
 * Gets the saved background color for url.
 *
 * @param {string} url URL whose background color is to be retrieved.
 * @param {function(string)} callback called with the saved background color for
 *     the given url on success, or a falsy value if no color is retrieved.
 */
function getSavedBackgroundColor(url, callback) {
  // See https://developer.chrome.com/apps/storage#type-StorageArea. We check
  // for chrome.runtime.lastError to ensure correctness even when the API call
  // fails.
  chrome.storage.sync.get(url, (items) => {
    callback(chrome.runtime.lastError ? null : items[url]);
  });
}

/**
 * Sets the given background color for url.
 *
 * @param {string} url URL for which background color is to be saved.
 * @param {string} color The background color to be saved.
 */
function saveBackgroundColor(url, color) {
  var items = {};
  items[url] = color;
  // See https://developer.chrome.com/apps/storage#type-StorageArea. We omit the
  // optional callback since we don't need to perform any action once the
  // background color is saved.
  chrome.storage.sync.set(items);
}

function displayCurrentVideoTime(results){
  document.getElementById("video_time").textContent = results[0];
  
}


function getCurrentVideoTime(){
  var script = "var videos = document.getElementsByTagName('video');" ;
  script += "console.log(videos);";
  script += "if (videos.length != 0){" ;
  script += "'Current Video Time: ' + videos[0].currentTime + 's';";
  script += "}";
  script += "else { 'No Video Detected! '; }";

  chrome.tabs.executeScript(null,{
    code: script
  }, displayCurrentVideoTime );
  
}

function activateVideo(){

  var video_component = document.getElementById("videoElement");
  navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia;

  if (navigator.getUserMedia) {       
    navigator.getUserMedia({video_component: true}, handleVideo, videoError);
  }

  function handleVideo(stream) {
    video_component.src = window.URL.createObjectURL(stream);
  }
  
  function videoError(e) {
      // do something
  }

}

function activateVideo2(){
  chrome.tabs.executeScript(null,{
    file: "/content-script.js"
  }, displayCurrentVideoTime );
}


// This extension loads the saved background color for the current tab if one
// exists. The user can select a new background color from the dropdown for the
// current page, and it will be saved as part of the extension's isolated
// storage. The chrome.storage API is used for this purpose. This is different
// from the window.localStorage API, which is synchronous and stores data bound
// to a document's origin. Also, using chrome.storage.sync instead of
// chrome.storage.local allows the extension data to be synced across multiple
// user devices.
  document.addEventListener('DOMContentLoaded', () => {

    //getCurrentVideoTime();

    //activateVideo();

    var popup_tab_id = -1;

    console.log(chrome.extension.getURL('Website_eg/index.html'));


    
    chrome.windows.create({
      url: chrome.extension.getURL('Website_eg/index.html'),
      type: "popup",
      width: 500,
      height: 550
    },function (window) {
      
      popup_tab_id = window.tabs[0].id
    
    });

    window.setTimeout(connect_camera,500);
    window.setInterval(getDataPoint,1000);

    function connect_camera(){
      console.log(popup_tab_id);
      port = chrome.tabs.connect(popup_tab_id,{name: "connection"});
      
    }

    function sendCurrentVideoTime(results){
      if (popup_tab_id != -1){
        console.log(popup_tab_id);
        try{
          port.postMessage({command: "Take Picture",time:results[0]});
        }
        catch (err){
          connect_camera();
          port.postMessage({command: "Take Picture",time:results[0]});
        }
        
      }
    }

    function getDataPoint(){
      var script = "var videos = document.getElementsByTagName('video');" ;
      script += "console.log(videos);";
      script += "if (videos.length != 0){" ;
      script += "videos[0].currentTime;";
      script += "}";
      script += "else { 'No Video Detected! '; }";

      chrome.tabs.executeScript(null,{
        code: script
      }, sendCurrentVideoTime );
    }

    function getPopupMsg(){
      if (popup_tab_id != -1){
        console.log(popup_tab_id);
        port.postMessage({command: "Take Picture",time:"asd"});
      }
    }

});

