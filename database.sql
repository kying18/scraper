DROP TABLE IF EXISTS sys.FacebookPosts;
DROP PROCEDURE IF EXISTS sys.InsertPost;

CREATE TABLE IF NOT EXISTS sys.FacebookPosts (
	id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, 
    post_text VARCHAR(10000) NOT NULL, 
    notified BOOL NOT NULL DEFAULT 0,
    source VARCHAR(50) NOT NULL);

SELECT * FROM sys.FacebookPosts;
-- UPDATE sys.FacebookPosts SET notified=1 WHERE id IN (1, 2, 3);

-- INSERT INTO sys.FacebookPosts (post_text, notified, source)
-- VALUE ('hi', 0, 'source');

-- REATE PROCEDURE InsertPost (IN post VARCHAR(255), IN src VARCHAR(50))
-- BEGIN
-- 	INSERT INTO sys.FacebookPosts (post_text, notified, source)
-- 	VALUES (post, 0, src);
-- END
-- select * from sys.FacebookPosts where post_text='hi' AND source='source'

DELIMITER $$

CREATE PROCEDURE sys.InsertPost (IN in_post varchar(10000),IN in_src_name varchar(50))
BEGIN
	IF NOT EXISTS (select * from sys.FacebookPosts where post_text=in_post AND source=in_src_name) THEN
		INSERT INTO sys.FacebookPosts (post_text, notified, source)
		VALUES (in_post, 0, in_src_name);
	END IF;
END
$$

DELIMITER ;

CALL sys.InsertPost('thisis a test pos', 'confessions');
-- 
-- SELECT * FROM sys.FacebookPosts;
