import 'dart:convert';
import 'dart:typed_data';

import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:travel_hub/services/tax_config_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  const sampleJson = '''
  {
    "Colombia": {
      "currency": "COP",
      "currencySymbol": "\$",
      "locale": "es_CO",
      "decimals": 0,
      "usdRate": 4200.0,
      "tax": {
        "name": "IVA",
        "rate": 0.19,
        "note": "Incluye IVA"
      }
    },
    "Estados Unidos": {
      "currency": "USD",
      "currencySymbol": "\$",
      "locale": "en_US",
      "decimals": 2,
      "usdRate": 1.0,
      "tax": {
        "name": "Hotel Tax",
        "rate": 0.12,
        "note": "Includes hotel tax"
      }
    }
  }
  ''';

  final messenger =
      TestDefaultBinaryMessengerBinding.instance.defaultBinaryMessenger;

  setUp(() {
    messenger.setMockMessageHandler('flutter/assets', (message) async {
      final assetKey = utf8.decode(message!.buffer.asUint8List());
      if (assetKey != 'assets/data/country_taxes.json') {
        return null;
      }

      final encoded = Uint8List.fromList(utf8.encode(sampleJson));
      return ByteData.view(encoded.buffer);
    });
  });

  tearDown(() {
    messenger.setMockMessageHandler('flutter/assets', null);
  });

  test('load parses country taxes from the bundled asset', () async {
    final config = await TaxConfigService.load();

    expect(config.keys, containsAll(['Colombia', 'Estados Unidos']));
    expect(config['Colombia']!.currency, 'COP');
    expect(config['Colombia']!.tax.rate, 0.19);
    expect(config['Estados Unidos']!.decimals, 2);
  });
}
