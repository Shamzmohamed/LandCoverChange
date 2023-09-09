function maskL8sr(image) {
  var cloudShadowBitMask = (1<< 3);
  var cloudsBitMask = (1<< 5); // Get the pixel QA band.
  var qa = image.select('pixel_qa');

// Feature Collection
var table = ee.FeatureCollection("users/shamzmohamed/muns_city");
// Both flags should be set to zero, indicating clear conditions.
var mask= qa.bitwiseAnd (cloudShadowBitMask).eq(0).and(qa.bitwiseAnd (cloudsBitMask).eq(0)); return image.updateMask(mask);}

//var dataset13 = ee. ImageCollection ('LANDSAT/LC08/C01/T1_SR') .filterDate('2013-01-01', '2013-12-31') .map(maskL8sr);
//var land8_13 = dataset13.mean().clip(table);
var dataset22 = ee. ImageCollection ('LANDSAT/LC08/C01/T1_SR') .filterDate('2022-01-01', '2022-12-31') .map(maskL8sr);
var land8 = dataset22.mean().clip(table);
var visParams = {
bands: ['B1','B2','B3','B4','B5','B6','B7'],min: 0,max: 3000,gamma: 1.4,};
print(land8)

// Zoom and set center
Map.setCenter(7.61, 51.9617, 11); 
Map.addLayer(land8, visParams);

// Export the data to drive as TIF
Export.image.toDrive({
  image: land8.select(['B1']),
  description: 'L8_B1_2022',
  folder: 'Mns',
  scale: 30, region: table,
  maxPixels: 1e13,
});