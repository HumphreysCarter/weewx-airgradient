## AQI calculation
##
##try

## PM2.5
#set $aqi = $current.ag_out_pm02_nowcast.raw
#if $aqi <= 50
    #set $pm02_aqi_category = "Good"
    #set $pm02_aqi_color = "#00e400"
#elif $aqi <= 100
    #set $pm02_aqi_category = "Moderate"
    #set $pm02_aqi_color = "#ffff00"
#elif $aqi <= 150
    #set $pm02_aqi_category = "Unhealthy for Sensitive Groups"
    #set $pm02_aqi_color = "#ff7e00"
#elif $aqi <= 200
    #set $pm02_aqi_category = "Unhealthy"
    #set $pm02_aqi_color = "#ff0000"
#elif $aqi <= 300
    #set $pm02_aqi_category = "Very Unhealthy"
    #set $pm02_aqi_color = "#8f3f97"
#else
    #set $pm02_aqi_category = "Hazardous"
    #set $pm02_aqi_color = "#7e0023"
#end if

## PM10
#set $aqi = $current.ag_out_pm10_nowcast.raw
#if $aqi <= 50
    #set $pm10_aqi_category = "Good"
    #set $pm10_aqi_color = "#00e400"
#elif $aqi <= 100
    #set $pm10_aqi_category = "Moderate"
    #set $pm10_aqi_color = "#ffff00"
#elif $aqi <= 150
    #set $pm10_aqi_category = "Unhealthy for Sensitive Groups"
    #set $pm10_aqi_color = "#ff7e00"
#elif $aqi <= 200
    #set $pm10_aqi_category = "Unhealthy"
    #set $pm10_aqi_color = "#ff0000"
#elif $aqi <= 300
    #set $pm10_aqi_category = "Very Unhealthy"
    #set $pm10_aqi_color = "#8f3f97"
#else
    #set $pm10_aqi_category = "Hazardous"
    #set $pm10_aqi_color = "#7e0023"
#end if

##except
##    #set $pm02_aqi_category = 'N/A'
##    #set $pm02_aqi_color = '#FFFFFF'
##   #set $pm10_aqi_category = 'N/A'
##    #set $pm10_aqi_color = '#FFFFFF'
##end try

##
##End AQI calculation

 <div id='airquality_widget' class="widget">
  <div class="widget_title">
    <a href="airquality.html">Air Quality</a>
    <a class="widget_control"
      onclick="toggle_widget('airquality')">&diams;</a>
  </div>

  <div class="widget_contents">
  <strong>Outdoor</strong>
  <table>
    <tbody>
      <tr>
        <td class="label">$obs.label.ag_out_pm02_nowcast</td>
        <td class="data">$current.ag_out_pm02_nowcast <span style="background-color: $pm02_aqi_color">($pm02_aqi_category)</span></td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_pm10_nowcast</td>
        <td class="data">$current.ag_out_pm10_nowcast <span style="background-color: $pm10_aqi_color">($pm10_aqi_category)</span></td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_atmp</td>
        <td class="data">$current.ag_out_atmp</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_rhum</td>
        <td class="data">$current.ag_out_rhum</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_rco2</td>
        <td class="data">$current.ag_out_rco2</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_pm01</td>
        <td class="data">$current.ag_out_pm01</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_pm02</td>
        <td class="data">$current.ag_out_pm02</td>
     </tr>
      <tr>
        <td class="label">$obs.label.ag_out_pm10</td>
        <td class="data">$current.ag_out_pm10</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_tvoc</td>
        <td class="data">$current.ag_out_tvoc</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_nox</td>
        <td class="data">$current.ag_out_nox</td>
      </tr>
    </tbody>
  </table>

    <strong>Indoor</strong>
  <table>
    <tbody>
          <tr>
        <td class="label">$obs.label.ag_in_atmp</td>
        <td class="data">$current.ag_in_atmp</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_in_rhum</td>
        <td class="data">$current.ag_in_rhum</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_in_rco2</td>
        <td class="data">$current.ag_in_rco2</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_in_pm01</td>
        <td class="data">$current.ag_in_pm01</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_in_pm02</td>
        <td class="data">$current.ag_in_pm02</td>
     </tr>
      <tr>
        <td class="label">$obs.label.ag_in_pm10</td>
        <td class="data">$current.ag_in_pm10</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_in_tvoc</td>
        <td class="data">$current.ag_in_tvoc</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_in_nox</td>
        <td class="data">$current.ag_in_nox</td>
      </tr>
    </tbody>
  </table>
  </div>

</div>
