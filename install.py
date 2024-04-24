from weecfg.extension import ExtensionInstaller


def loader():
    return AirGradientInstaller()


class AirGradientInstaller(ExtensionInstaller):
    def __init__(self):
        super(AirGradientInstaller, self).__init__(
            version="0.1",
            name='airgradient',
            description='Data ingest for AirGradient air quality monitors.',
            author="Carter Humphreys",
            author_email="carter.humphreys@lake-effect.dev",
            process_services='user.airgradient.IngestAirGradientData',
            config={
                'AirGradient': {
                    'outdoor_sensor_ip': '0.0.0.0',
                    'indoor_sensor_ip': '0.0.0.0',
                },
            },
            files=[('bin/user', ['bin/user/airgradient.py']), ]
        )
