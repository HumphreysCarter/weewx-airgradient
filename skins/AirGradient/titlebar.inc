## titlebar for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo
#encoding UTF-8

#set $show_rss = $to_bool($DisplayOptions.get('show_rss', True))
#set $show_reports = $to_bool($DisplayOptions.get('show_reports', True))

<div id="title_bar">
  <div id="title">
    <h1 class="page_title">Air Quality - $station.location</h1>
    <p class="lastupdate">$current.dateTime</p>
  </div>
</div>
