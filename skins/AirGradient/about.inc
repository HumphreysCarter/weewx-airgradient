## about module for weewx skins
## Copyright Tom Keffer, Matthew Wall
## See LICENSE.txt for your rights
#errorCatcher Echo
#encoding UTF-8

<div id='about_widget' class="widget">
  <div class="widget_title">
    $gettext("About this station")
    <a class="widget_control"
      onclick="toggle_widget('about')">&diams;</a>
  </div>
  <div class="widget_contents">
  <table>
    <tr>
      <td class="label">$gettext("Server uptime")</td>
      <td class="data">$station.os_uptime.long_form</td>
    </tr>
    <tr>
      <td class="label">$gettext("WeeWX uptime")</td>
      <td class="data">$station.uptime.long_form</td>
    </tr>
    <tr>
      <td class="label">$gettext("WeeWX version")</td>
      <td class="data">$station.version</td>
    </tr>
    <tr>
      <td class="label">$gettext("Skin")</td>
      <td class="data">$SKIN_NAME $SKIN_VERSION</td>
    </tr>
  </table>
  </div>

</div>
