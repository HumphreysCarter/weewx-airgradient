## AQI calculation
##
#try
    #set $pm02_24hr_mean = $span($time_delta=86400).ag_out_pm02.avg.raw

    ## Calculate raw US AQI value
    #if $pm02_24hr_mean <= 12.0
        #set $AQI_US = ((50 - 0) / (12.0 - 0) * ($pm02_24hr_mean - 0) + 0)
    #elif $pm02_24hr_mean <= 35.4
        #set $AQI_US = ((100 - 50) / (35.4 - 12.0) * ($pm02_24hr_mean - 12.0) + 50)
    #elif $pm02_24hr_mean <= 55.4
        #set $AQI_US = ((150 - 100) / (55.4 - 35.4) * ($pm02_24hr_mean - 35.4) + 100)
    #elif $pm02_24hr_mean <= 150.4
        #set $AQI_US = ((200 - 150) / (150.4 - 55.4) * ($pm02_24hr_mean - 55.4) + 150)
    #elif $pm02_24hr_mean <= 250.4
        #set $AQI_US = ((300 - 200) / (250.4 - 150.4) * ($pm02_24hr_mean - 150.4) + 200)
    #elif $pm02_24hr_mean <= 350.4
        #set $AQI_US = ((400 - 300) / (350.4 - 250.4) * ($pm02_24hr_mean - 250.4) + 300)
    #elif $pm02_24hr_mean <= 500.4
        #set $AQI_US = ((500 - 400) / (500.4 - 350.4) * ($pm02_24hr_mean - 350.4) + 400)
    #else
        #set $AQI_US = 500
    #end if

    ## Round AQI to a whole number
    #set $AQI_US = round($AQI_US)

    ## Calculate US AQI category and corresponding color from raw AQI
    #if $AQI_US <= 50
        #set $AQI_US_Category = "Good"
        #set $AQI_US_Color = "#00e400"
    #elif $AQI_US <= 100
        #set $AQI_US_Category = "Moderate"
        #set $AQI_US_Color = "#ffff00"
    #elif $AQI_US <= 150
        #set $AQI_US_Category = "Unhealthy for Sensitive Groups"
        #set $AQI_US_Color = "#ff7e00"
    #elif $AQI_US <= 200
        #set $AQI_US_Category = "Unhealthy"
        #set $AQI_US_Color = "#ff0000"
    #elif $AQI_US <= 300
        #set $AQI_US_Category = "Very Unhealthy"
        #set $AQI_US_Color = "#8f3f97"
    #else
        #set $AQI_US_Category = "Hazardous"
        #set $AQI_US_Color = "#7e0023"
    #end if

#except
    #set $AQI_US = 'N/A'
    #set $AQI_US_Category = 'N/A'
    #set $AQI_US_Color = '#FFFFFF'
#end try
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
        <td class="label">AQI</td>
        <td class="data">$AQI_US <span style="background-color: $AQI_US_Color">($AQI_US_Category)</span></td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_pm02_aqi</td>
        <td class="data">$current.ag_out_pm02_aqi</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_pm10_aqi</td>
        <td class="data">$current.ag_out_pm10_aqi</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_pm02_nowcast</td>
        <td class="data">$current.ag_out_pm02_nowcast</td>
      </tr>
      <tr>
        <td class="label">$obs.label.ag_out_pm10_nowcast</td>
        <td class="data">$current.ag_out_pm10_nowcast</td>
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
