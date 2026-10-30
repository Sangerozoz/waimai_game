export interface VehicleArt { readonly tier:number; readonly grade:string; readonly name:string; readonly resource:string }

const names=['旧电动车','翻新电动车','品牌电动车','长续航电动车','大箱摩托车','运动摩托车','豪华摩托车','限量豪华摩托车','黄金限量摩托车','至尊飞行摩托车 · 隐藏'];
const grades=['D','D+','C','C+','B','B+','A','S','SS','SSS'];
const files=['d','d-plus','c','c-plus','b','b-plus','a','s','ss','sss'];
export const MAP_VEHICLES:ReadonlyArray<VehicleArt>=Object.freeze(names.map((name,index)=>Object.freeze({tier:index+1,grade:grades[index],name,resource:`map-sample/vehicles/top-${files[index]}`})));

export function vehicleArtForTier(tier:number):VehicleArt {
  return MAP_VEHICLES.filter(art=>art.tier===tier)[0]||MAP_VEHICLES[0];
}
