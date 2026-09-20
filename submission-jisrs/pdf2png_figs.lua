-- Rewrite figure references from vector .pdf to raster .png so that
-- images embed correctly in the Word (.docx) output.
function Image(el)
  el.src = el.src:gsub("%.pdf$", ".png")
  return el
end
