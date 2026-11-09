/** Shared spacing in the 720px design canvas; presentation only. */
export const V2_SPACE={page:18,card:12,imageInset:8,imageText:12,buttonEdge:10,gap:12,lineHeight:1.3};
export const V2_CONTENT=720-2*V2_SPACE.page;
export function columnWidth(columns:number,gap=V2_SPACE.gap,width=V2_CONTENT):number {
 return (width-(columns-1)*gap)/columns;
}

/** Approved master measurements projected into the 720×1280 canvas. */
export const V2_LAYOUT={
 riderCardHeight:180,riderRowGap:8,riderTop:120,riderBottom:1431,
 vehicleTileHeight:194,vehicleRowStep:205,
 mapHeight:202,mapRowStep:215,mapInset:4,
};
