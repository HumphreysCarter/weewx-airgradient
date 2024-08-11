  <style>
    .aqi-bar {
      display: flex;
      width: 330px;
      position: relative;
    }
    .aqi-bar span {
      display: inline-block;
      height: 10px;
    }
    .pointer {
      position: absolute;
      text-align: center;
      font-size: 14px;
      top: 4px; /* Adjust top positioning to move the pointer down */
      transform: translateX(-50%); /* Center the pointer */
    }
    .data {
      text-align: center; /* Center-align data cell content */
    }
    .data .aqi-bar {
      margin: 0 auto; /* Center the bar within the cell */
    }
  </style>
  <script>
    function positionPointer(aqi, pointerId, barId) {
      const aqiBar = document.getElementById(barId);
      const aqiBarLength = aqiBar.offsetWidth; // Total length of the AQI bar in pixels
      const aqiSegments = [50, 50, 50, 50, 100, 200]; // AQI segments
      const segmentWidths = [
        aqiBarLength * (50 / 500),
        aqiBarLength * (50 / 500),
        aqiBarLength * (50 / 500),
        aqiBarLength * (50 / 500),
        aqiBarLength * (100 / 500),
        aqiBarLength * (200 / 500)
      ]; // Widths of each segment in pixels

      let cumulativeLength = 0;
      let pointerPosition = 0;

      for (let i = 0; i < aqiSegments.length; i++) {
        if (aqi <= cumulativeLength + aqiSegments[i]) {
          const segmentStart = cumulativeLength;
          const segmentEnd = cumulativeLength + aqiSegments[i];
          const positionInSegment = ((aqi - segmentStart) / (segmentEnd - segmentStart)) * segmentWidths[i];
          pointerPosition += positionInSegment;
          break;
        } else {
          pointerPosition += segmentWidths[i];
          cumulativeLength += aqiSegments[i];
        }
      }

      const pointerElement = document.getElementById(pointerId);
      pointerElement.style.left = pointerPosition + 'px';
    }

    window.onload = function() {
      #for $sensor in $Extras.sensors
        // Retrieve AQI values for PM2.5 and PM10
        var aqi24h_pm25_${sensor} = ${latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_pm02_aqi')};
        var aqiNowCast_pm25_${sensor} = ${latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_pm02_nowcast')};
        var aqi24h_pm10_${sensor} = ${latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_pm10_aqi')};
        var aqiNowCast_pm10_${sensor} = ${latest('airgradient_binding').__getattr__('airquality_' + $sensor + '_pm10_nowcast')};

        // Position the pointers for each sensor
        positionPointer(aqi24h_pm25_${sensor}, 'pointer24h_pm25_${sensor}', 'aqi_bar_24h_pm25_${sensor}');
        positionPointer(aqiNowCast_pm25_${sensor}, 'pointerNowCast_pm25_${sensor}', 'aqi_bar_nowcast_pm25_${sensor}');
        positionPointer(aqi24h_pm10_${sensor}, 'pointer24h_pm10_${sensor}', 'aqi_bar_24h_pm10_${sensor}');
        positionPointer(aqiNowCast_pm10_${sensor}, 'pointerNowCast_pm10_${sensor}', 'aqi_bar_nowcast_pm10_${sensor}');
      #end for
    };

  </script>

<div id='aqi_widget' class="widget">
  <div class="widget_title">
    Air Quality Index
    <a class="widget_control" onclick="toggle_widget('aqi')">&diams;</a>
  </div>

  <div class="widget_contents">
    #for $sensor in $Extras.sensors
      <br>
      <strong>$sensor</strong>

      <!-- PM2.5 Section -->
      <div id="aqi_bar_24h_pm25_# $sensor" style="margin-top:10px;margin-bottom:0px;">
        <div style="text-align:left;margin-bottom:15px;margin-left:7px;">
          <table>
            <tbody>
              <tr>
                <td class="label" rowspan="2" style="vertical-align:middle; text-align:center;"><strong>PM<br>2.5</strong></td>
                <td class="label">24h AQI</td>
                <td class="data" style="position: relative;">
                  <div class="aqi-bar" id="aqi_bar_24h_pm25_${sensor}">
                    <span style="width:33px;background-color:#008000;"></span>
                    <span style="width:33px;background-color:#FFFF00;"></span>
                    <span style="width:33px;background-color:#FF8C00;"></span>
                    <span style="width:33px;background-color:#FF0000;"></span>
                    <span style="width:66px;background-color:#800080;"></span>
                    <span style="width:132px;background-color:#800000;"></span>
                    <div id="pointer24h_pm25_${sensor}" class="pointer">▲</div>
                  </div>
                </td>
              </tr>
              <tr>
                <td class="label">NowCast</td>
                <td class="data" style="position: relative;">
                  <div class="aqi-bar" id="aqi_bar_nowcast_pm25_${sensor}">
                    <span style="width:33px;background-color:#008000;"></span>
                    <span style="width:33px;background-color:#FFFF00;"></span>
                    <span style="width:33px;background-color:#FF8C00;"></span>
                    <span style="width:33px;background-color:#FF0000;"></span>
                    <span style="width:66px;background-color:#800080;"></span>
                    <span style="width:132px;background-color:#800000;"></span>
                    <div id="pointerNowCast_pm25_${sensor}" class="pointer">▲</div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- PM10 Section -->
      <div id="aqi_bar_24h_pm10_# $sensor" style="margin-top:10px;margin-bottom:0px;">
        <div style="text-align:left;margin-bottom:15px;margin-left:7px;">
          <table>
            <tbody>
              <tr>
                <td class="label" rowspan="2" style="vertical-align:middle; text-align:center;"><strong>PM<br>10</strong></td>
                <td class="label">24h AQI</td>
                <td class="data" style="position: relative;">
                  <div class="aqi-bar" id="aqi_bar_24h_pm10_${sensor}">
                    <span style="width:33px;background-color:#008000;"></span>
                    <span style="width:33px;background-color:#FFFF00;"></span>
                    <span style="width:33px;background-color:#FF8C00;"></span>
                    <span style="width:33px;background-color:#FF0000;"></span>
                    <span style="width:66px;background-color:#800080;"></span>
                    <span style="width:132px;background-color:#800000;"></span>
                    <div id="pointer24h_pm10_${sensor}" class="pointer">▲</div>
                  </div>
                </td>
              </tr>
              <tr>
                <td class="label">NowCast</td>
                <td class="data" style="position: relative;">
                  <div class="aqi-bar" id="aqi_bar_nowcast_pm10_${sensor}">
                    <span style="width:33px;background-color:#008000;"></span>
                    <span style="width:33px;background-color:#FFFF00;"></span>
                    <span style="width:33px;background-color:#FF8C00;"></span>
                    <span style="width:33px;background-color:#FF0000;"></span>
                    <span style="width:66px;background-color:#800080;"></span>
                    <span style="width:132px;background-color:#800000;"></span>
                    <div id="pointerNowCast_pm10_${sensor}" class="pointer">▲</div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    #end for
  </div>
</div>
