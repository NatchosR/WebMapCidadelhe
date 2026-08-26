var wms_layers = [];


        var lyr_GoogleSatellite_0 = new ol.layer.Tile({
            'title': 'Google Satellite',
            'opacity': 1.000000,
            
            
            source: new ol.source.XYZ({
            attributions: ' ',
                url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}'
            })
        });
var format_alagoa_line_1 = new ol.format.GeoJSON();
var features_alagoa_line_1 = format_alagoa_line_1.readFeatures(json_alagoa_line_1, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_alagoa_line_1 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_alagoa_line_1.addFeatures(features_alagoa_line_1);
var lyr_alagoa_line_1 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_alagoa_line_1, 
                style: style_alagoa_line_1,
                popuplayertitle: 'alagoa_line',
                interactive: false,
                title: '<img src="styles/legend/alagoa_line_1.png" /> alagoa_line'
            });
var format_carrascal_line_2 = new ol.format.GeoJSON();
var features_carrascal_line_2 = format_carrascal_line_2.readFeatures(json_carrascal_line_2, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_carrascal_line_2 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_carrascal_line_2.addFeatures(features_carrascal_line_2);
var lyr_carrascal_line_2 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_carrascal_line_2, 
                style: style_carrascal_line_2,
                popuplayertitle: 'carrascal_line',
                interactive: false,
                title: '<img src="styles/legend/carrascal_line_2.png" /> carrascal_line'
            });
var format_lagar_line_3 = new ol.format.GeoJSON();
var features_lagar_line_3 = format_lagar_line_3.readFeatures(json_lagar_line_3, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_lagar_line_3 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_lagar_line_3.addFeatures(features_lagar_line_3);
var lyr_lagar_line_3 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_lagar_line_3, 
                style: style_lagar_line_3,
                popuplayertitle: 'lagar_line',
                interactive: false,
                title: '<img src="styles/legend/lagar_line_3.png" /> lagar_line'
            });
var format_trees_all_4 = new ol.format.GeoJSON();
var features_trees_all_4 = format_trees_all_4.readFeatures(json_trees_all_4, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_trees_all_4 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_trees_all_4.addFeatures(features_trees_all_4);
var lyr_trees_all_4 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_trees_all_4, 
                style: style_trees_all_4,
                popuplayertitle: 'trees_all',
                interactive: false,
    title: 'trees_all<br />\
    <img src="styles/legend/trees_all_4_0.png" /> Emergente<br />\
    <img src="styles/legend/trees_all_4_1.png" /> High<br />\
    <img src="styles/legend/trees_all_4_2.png" /> Support<br />\
    <img src="styles/legend/trees_all_4_3.png" /> Fig and Olive<br />' });
var format_existing_trees_5 = new ol.format.GeoJSON();
var features_existing_trees_5 = format_existing_trees_5.readFeatures(json_existing_trees_5, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_existing_trees_5 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_existing_trees_5.addFeatures(features_existing_trees_5);
var lyr_existing_trees_5 = new ol.layer.Vector({
                declutter: false,
                source:jsonSource_existing_trees_5, 
                style: style_existing_trees_5,
                popuplayertitle: 'existing_trees',
                interactive: false,
                title: '<img src="styles/legend/existing_trees_5.png" /> existing_trees'
            });
var group_lagar = new ol.layer.Group({
                                layers: [lyr_lagar_line_3,],
                                fold: "open",
                                title: 'lagar'});
var group_carrascal = new ol.layer.Group({
                                layers: [lyr_carrascal_line_2,],
                                fold: "open",
                                title: 'carrascal'});
var group_alagoa = new ol.layer.Group({
                                layers: [lyr_alagoa_line_1,],
                                fold: "open",
                                title: 'alagoa'});

lyr_GoogleSatellite_0.setVisible(true);lyr_alagoa_line_1.setVisible(true);lyr_carrascal_line_2.setVisible(true);lyr_lagar_line_3.setVisible(true);lyr_trees_all_4.setVisible(true);lyr_existing_trees_5.setVisible(true);
var layersList = [lyr_GoogleSatellite_0,group_alagoa,group_carrascal,group_lagar,lyr_trees_all_4,lyr_existing_trees_5];
lyr_alagoa_line_1.set('fieldAliases', {'fid': 'fid', 'referenced_line': 'referenced_line', 'instance': 'instance', 'offset': 'offset', 'length': 'length', });
lyr_carrascal_line_2.set('fieldAliases', {'fid': 'fid', 'referenced_line': 'referenced_line', 'instance': 'instance', 'offset': 'offset', 'length': 'length', });
lyr_lagar_line_3.set('fieldAliases', {'fid': 'fid', 'referenced_line': 'referenced_line', 'length': 'length', 'offset': 'offset', 'instance': 'instance', });
lyr_trees_all_4.set('fieldAliases', {'fid': 'fid', 'offset': 'offset', 'instance': 'instance', 'schema_offset': 'schema_offset', 'distance_m': 'distance_m', 'cycle_position': 'cycle_position', 'species': 'species', 'category': 'category', 'land': 'land', });
lyr_existing_trees_5.set('fieldAliases', {'fid': 'fid', });
lyr_alagoa_line_1.set('fieldImages', {'fid': 'TextEdit', 'referenced_line': 'TextEdit', 'instance': 'Range', 'offset': 'TextEdit', 'length': 'TextEdit', });
lyr_carrascal_line_2.set('fieldImages', {'fid': 'TextEdit', 'referenced_line': 'TextEdit', 'instance': 'Range', 'offset': 'TextEdit', 'length': 'TextEdit', });
lyr_lagar_line_3.set('fieldImages', {'fid': 'TextEdit', 'referenced_line': 'TextEdit', 'length': 'TextEdit', 'offset': 'TextEdit', 'instance': 'Range', });
lyr_trees_all_4.set('fieldImages', {'fid': 'TextEdit', 'offset': 'TextEdit', 'instance': 'TextEdit', 'schema_offset': 'TextEdit', 'distance_m': 'TextEdit', 'cycle_position': 'Range', 'species': 'TextEdit', 'category': 'TextEdit', 'land': 'TextEdit', });
lyr_existing_trees_5.set('fieldImages', {'fid': 'TextEdit', });
lyr_alagoa_line_1.set('fieldLabels', {'fid': 'no label', 'referenced_line': 'no label', 'instance': 'no label', 'offset': 'no label', 'length': 'no label', });
lyr_carrascal_line_2.set('fieldLabels', {'fid': 'no label', 'referenced_line': 'no label', 'instance': 'no label', 'offset': 'no label', 'length': 'no label', });
lyr_lagar_line_3.set('fieldLabels', {'fid': 'hidden field', 'referenced_line': 'hidden field', 'length': 'header label - always visible', 'offset': 'hidden field', 'instance': 'hidden field', });
lyr_trees_all_4.set('fieldLabels', {'fid': 'no label', 'offset': 'no label', 'instance': 'no label', 'schema_offset': 'no label', 'distance_m': 'no label', 'cycle_position': 'no label', 'species': 'no label', 'category': 'no label', 'land': 'no label', });
lyr_existing_trees_5.set('fieldLabels', {'fid': 'no label', });
lyr_existing_trees_5.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});