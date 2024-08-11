
 <div id='airquality_widget' class="widget">
  <div class="widget_title">
    Air Quality Data
    <a class="widget_control"
      onclick="toggle_widget('airquality')">&diams;</a>
  </div>

  <div class="widget_contents">
 
    #for $sensor in $Extras.sensors
      <br>
      <strong>$sensor</strong>
      <table>
        <tbody>
          <tr>
            <td class="label">PM1.0</td>
            <td class="data">$latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_pm01')</td>
          </tr>
          <tr>
            <td class="label">PM2.5</td>
            <td class="data">$latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_pm02')</td>
          </tr>
          <tr>
            <td class="label">PM10</td>
            <td class="data">$latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_pm10')</td>
          </tr>
          <tr>
            <td class="label">PM 0.3 Count</td>
            <td class="data">$latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_pm003_count')</td>
          </tr>
          <tr>
            <td class="label">CO<sub>2</sub></td>
            <td class="data">$latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_rco2')</td>
          </tr>
          <tr>
            <td class="label">TVOC</td>
            <td class="data">$latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_tvoc_raw')</td>
          </tr>
          <tr>
            <td class="label">NOx</td>
            <td class="data">$latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_nox_raw')</td>
          </tr>
        </tbody>
      </table>
    #end for

  </div>

</div>
