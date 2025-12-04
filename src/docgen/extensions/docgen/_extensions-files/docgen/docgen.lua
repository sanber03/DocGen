-- function Meta(meta)
--   print("=== META FUNCTION CALLED FIRST ===")
  
--   return meta
-- end

-- function Pandoc(doc)
--   -- Initialize counters from metadata if they exist
--   return doc
-- end


-- function Header(el)
--   print("Header function called - Level " .. el.level .. " - CWD: " .. global_meta.dynotec_original_cwd)
--   return el
-- end

-- function Image(el)
--   print("Img function called - CWD: " .. pandoc.utils.stringify(el.src))
--   return el
-- end


-- -- Return the filters in the correct order
-- return {
--   { Meta = Meta },
--   { Header = Header },
--   { Image = Image },
--   { Pandoc = Pandoc },
-- }