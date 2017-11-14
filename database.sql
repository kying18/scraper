CREATE TABLE IF NOT EXISTS sys.FacebookPosts (
	id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    post_text VARCHAR(255) NOT NULL, 
    notified BOOL NOT NULL DEFAULT 0,
    source VARCHAR(50) NOT NULL);

SELECT * FROM sys.FacebookPosts;

INSERT INTO sys.FacebookPosts (post_text, notified, source)
VALUE ('hi', 0, 'source');

-- REATE PROCEDURE InsertPost (IN post VARCHAR(255), IN src VARCHAR(50))
-- BEGIN
-- 	INSERT INTO sys.FacebookPosts (post_text, notified, source)
-- 	VALUES (post, 0, src);
-- END
    
CREATE PROCEDURE sys.InsertPost (IN post varchar(255),IN src_name varchar(50))
BEGIN
    INSERT INTO sys.FacebookPosts (post_text, notified, source) VALUES (post, 0, src_name);
END