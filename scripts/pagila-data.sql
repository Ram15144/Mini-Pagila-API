--
-- PostgreSQL database dump
-- Pagila Sample Database Data
-- Enhanced version for Pagila API testing
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

SET search_path = public, pg_catalog;

-- Temporarily disable foreign key checks to allow safe loading
SET session_replication_role = replica;
--
-- Data for Name: language; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO language (language_id, name, last_update) VALUES
(1, 'English             ', '2006-02-15 10:02:19'),
(2, 'Italian             ', '2006-02-15 10:02:19'),
(3, 'Japanese            ', '2006-02-15 10:02:19'),
(4, 'Mandarin            ', '2006-02-15 10:02:19'),
(5, 'French              ', '2006-02-15 10:02:19'),
(6, 'German              ', '2006-02-15 10:02:19');

--
-- Data for Name: country; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO country (country_id, country, last_update) VALUES
(1, 'Afghanistan', '2006-02-15 09:44:00'),
(2, 'Algeria', '2006-02-15 09:44:00'),
(3, 'American Samoa', '2006-02-15 09:44:00'),
(4, 'Angola', '2006-02-15 09:44:00'),
(5, 'Anguilla', '2006-02-15 09:44:00'),
(6, 'Argentina', '2006-02-15 09:44:00'),
(7, 'Armenia', '2006-02-15 09:44:00'),
(8, 'Australia', '2006-02-15 09:44:00'),
(9, 'Austria', '2006-02-15 09:44:00'),
(10, 'Azerbaijan', '2006-02-15 09:44:00'),
(11, 'Bahrain', '2006-02-15 09:44:00'),
(12, 'Bangladesh', '2006-02-15 09:44:00'),
(13, 'Belarus', '2006-02-15 09:44:00'),
(14, 'Bolivia', '2006-02-15 09:44:00'),
(15, 'Brazil', '2006-02-15 09:44:00'),
(16, 'Brunei', '2006-02-15 09:44:00'),
(17, 'Bulgaria', '2006-02-15 09:44:00'),
(18, 'Cambodia', '2006-02-15 09:44:00'),
(19, 'Cameroon', '2006-02-15 09:44:00'),
(20, 'Canada', '2006-02-15 09:44:00'),
(21, 'Chad', '2006-02-15 09:44:00'),
(22, 'Chile', '2006-02-15 09:44:00'),
(23, 'China', '2006-02-15 09:44:00'),
(24, 'Colombia', '2006-02-15 09:44:00'),
(25, 'Czech Republic', '2006-02-15 09:44:00'),
(26, 'Dominican Republic', '2006-02-15 09:44:00'),
(27, 'Ecuador', '2006-02-15 09:44:00'),
(28, 'Egypt', '2006-02-15 09:44:00'),
(29, 'Estonia', '2006-02-15 09:44:00'),
(30, 'Ethiopia', '2006-02-15 09:44:00'),
(31, 'Faroe Islands', '2006-02-15 09:44:00'),
(32, 'Finland', '2006-02-15 09:44:00'),
(33, 'France', '2006-02-15 09:44:00'),
(34, 'French Guiana', '2006-02-15 09:44:00'),
(35, 'French Polynesia', '2006-02-15 09:44:00'),
(36, 'Gambia', '2006-02-15 09:44:00'),
(37, 'Germany', '2006-02-15 09:44:00'),
(38, 'Greece', '2006-02-15 09:44:00'),
(39, 'Greenland', '2006-02-15 09:44:00'),
(40, 'Holy See (Vatican City State)', '2006-02-15 09:44:00'),
(41, 'Hong Kong', '2006-02-15 09:44:00'),
(42, 'Hungary', '2006-02-15 09:44:00'),
(43, 'India', '2006-02-15 09:44:00'),
(44, 'Indonesia', '2006-02-15 09:44:00'),
(45, 'Iran', '2006-02-15 09:44:00'),
(46, 'Iraq', '2006-02-15 09:44:00'),
(47, 'Israel', '2006-02-15 09:44:00'),
(48, 'Italy', '2006-02-15 09:44:00'),
(49, 'Japan', '2006-02-15 09:44:00'),
(50, 'Kazakhstan', '2006-02-15 09:44:00'),
(51, 'Kenya', '2006-02-15 09:44:00'),
(52, 'Kuwait', '2006-02-15 09:44:00'),
(53, 'Latvia', '2006-02-15 09:44:00'),
(54, 'Liechtenstein', '2006-02-15 09:44:00'),
(55, 'Lithuania', '2006-02-15 09:44:00'),
(56, 'Madagascar', '2006-02-15 09:44:00'),
(57, 'Malawi', '2006-02-15 09:44:00'),
(58, 'Malaysia', '2006-02-15 09:44:00'),
(59, 'Mexico', '2006-02-15 09:44:00'),
(60, 'Moldova', '2006-02-15 09:44:00'),
(61, 'Morocco', '2006-02-15 09:44:00'),
(62, 'Myanmar', '2006-02-15 09:44:00'),
(63, 'Nauru', '2006-02-15 09:44:00'),
(64, 'Nepal', '2006-02-15 09:44:00'),
(65, 'Netherlands', '2006-02-15 09:44:00'),
(66, 'New Zealand', '2006-02-15 09:44:00'),
(67, 'Nigeria', '2006-02-15 09:44:00'),
(68, 'North Korea', '2006-02-15 09:44:00'),
(69, 'Oman', '2006-02-15 09:44:00'),
(70, 'Pakistan', '2006-02-15 09:44:00'),
(71, 'Paraguay', '2006-02-15 09:44:00'),
(72, 'Peru', '2006-02-15 09:44:00'),
(73, 'Philippines', '2006-02-15 09:44:00'),
(74, 'Poland', '2006-02-15 09:44:00'),
(75, 'Puerto Rico', '2006-02-15 09:44:00'),
(76, 'Romania', '2006-02-15 09:44:00'),
(77, 'Runion', '2006-02-15 09:44:00'),
(78, 'Russian Federation', '2006-02-15 09:44:00'),
(79, 'Saint Vincent and the Grenadines', '2006-02-15 09:44:00'),
(80, 'Saudi Arabia', '2006-02-15 09:44:00'),
(81, 'Senegal', '2006-02-15 09:44:00'),
(82, 'Slovakia', '2006-02-15 09:44:00'),
(83, 'South Africa', '2006-02-15 09:44:00'),
(84, 'South Korea', '2006-02-15 09:44:00'),
(85, 'Spain', '2006-02-15 09:44:00'),
(86, 'Sri Lanka', '2006-02-15 09:44:00'),
(87, 'Sudan', '2006-02-15 09:44:00'),
(88, 'Sweden', '2006-02-15 09:44:00'),
(89, 'Switzerland', '2006-02-15 09:44:00'),
(90, 'Taiwan', '2006-02-15 09:44:00'),
(91, 'Tanzania', '2006-02-15 09:44:00'),
(92, 'Thailand', '2006-02-15 09:44:00'),
(93, 'Tonga', '2006-02-15 09:44:00'),
(94, 'Tunisia', '2006-02-15 09:44:00'),
(95, 'Turkey', '2006-02-15 09:44:00'),
(96, 'Turkmenistan', '2006-02-15 09:44:00'),
(97, 'Tuvalu', '2006-02-15 09:44:00'),
(98, 'Ukraine', '2006-02-15 09:44:00'),
(99, 'United Arab Emirates', '2006-02-15 09:44:00'),
(100, 'United Kingdom', '2006-02-15 09:44:00'),
(101, 'United States', '2006-02-15 09:44:00'),
(102, 'Venezuela', '2006-02-15 09:44:00'),
(103, 'Vietnam', '2006-02-15 09:44:00'),
(104, 'Virgin Islands, U.S.', '2006-02-15 09:44:00'),
(105, 'Yemen', '2006-02-15 09:44:00'),
(106, 'Yugoslavia', '2006-02-15 09:44:00'),
(107, 'Zambia', '2006-02-15 09:44:00');

--
-- Data for Name: city; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO city (city_id, city, country_id, last_update) VALUES
(1, 'A Corua (La Corua)', 85, '2006-02-15 09:45:25'),
(2, 'Abha', 80, '2006-02-15 09:45:25'),
(3, 'Abu Dhabi', 99, '2006-02-15 09:45:25'),
(4, 'Acua', 59, '2006-02-15 09:45:25'),
(5, 'Adana', 95, '2006-02-15 09:45:25'),
(6, 'Addis Abeba', 30, '2006-02-15 09:45:25'),
(7, 'Aden', 105, '2006-02-15 09:45:25'),
(8, 'Adoni', 43, '2006-02-15 09:45:25'),
(9, 'Ahmadnagar', 43, '2006-02-15 09:45:25'),
(10, 'Akishima', 49, '2006-02-15 09:45:25'),
(11, 'Akron', 101, '2006-02-15 09:45:25'),
(12, 'al-Ayn', 99, '2006-02-15 09:45:25'),
(13, 'al-Hawiya', 80, '2006-02-15 09:45:25'),
(14, 'al-Manama', 11, '2006-02-15 09:45:25'),
(15, 'al-Qadarif', 87, '2006-02-15 09:45:25'),
(16, 'al-Qatif', 80, '2006-02-15 09:45:25'),
(17, 'Alessandria', 48, '2006-02-15 09:45:25'),
(18, 'Allappuzha (Alleppey)', 43, '2006-02-15 09:45:25'),
(19, 'Allende', 59, '2006-02-15 09:45:25'),
(20, 'Almirante Brown', 6, '2006-02-15 09:45:25'),
(21, 'Alvorada', 15, '2006-02-15 09:45:25'),
(22, 'Ambattur', 43, '2006-02-15 09:45:25'),
(23, 'Amersfoort', 65, '2006-02-15 09:45:25'),
(24, 'Amroha', 43, '2006-02-15 09:45:25'),
(25, 'Angeles', 73, '2006-02-15 09:45:25'),
(26, 'Angers', 33, '2006-02-15 09:45:25'),
(27, 'Anpolis', 15, '2006-02-15 09:45:25'),
(28, 'Antofagasta', 22, '2006-02-15 09:45:25'),
(29, 'Aparecida de Goinia', 15, '2006-02-15 09:45:25'),
(30, 'Apeldoorn', 65, '2006-02-15 09:45:25'),
(31, 'Araatuba', 15, '2006-02-15 09:45:25'),
(32, 'Arak', 45, '2006-02-15 09:45:25'),
(33, 'Arecibo', 75, '2006-02-15 09:45:25'),
(34, 'Arlington', 101, '2006-02-15 09:45:25'),
(35, 'Ashdod', 47, '2006-02-15 09:45:25'),
(36, 'Ashgabat', 96, '2006-02-15 09:45:25'),
(37, 'Ashqelon', 47, '2006-02-15 09:45:25'),
(38, 'Asuncin', 71, '2006-02-15 09:45:25'),
(39, 'Athenai', 38, '2006-02-15 09:45:25'),
(40, 'Atinsk', 78, '2006-02-15 09:45:25'),
(41, 'Atlixco', 59, '2006-02-15 09:45:25'),
(42, 'Augusta-Richmond County', 101, '2006-02-15 09:45:25'),
(43, 'Aurora', 101, '2006-02-15 09:45:25'),
(44, 'Avellaneda', 6, '2006-02-15 09:45:25'),
(45, 'Bag', 15, '2006-02-15 09:45:25'),
(46, 'Baha Blanca', 6, '2006-02-15 09:45:25'),
(47, 'Baicheng', 23, '2006-02-15 09:45:25'),
(48, 'Baiyin', 23, '2006-02-15 09:45:25'),
(49, 'Baku', 10, '2006-02-15 09:45:25'),
(50, 'Balurghat', 43, '2006-02-15 09:45:25'),
(51, 'Bamenda', 19, '2006-02-15 09:45:25'),
(52, 'Bandar Seri Begawan', 16, '2006-02-15 09:45:25'),
(53, 'Banjul', 36, '2006-02-15 09:45:25'),
(54, 'Barcelona', 102, '2006-02-15 09:45:25'),
(55, 'Basel', 89, '2006-02-15 09:45:25'),
(56, 'Bat Yam', 47, '2006-02-15 09:45:25'),
(57, 'Batman', 95, '2006-02-15 09:45:25'),
(58, 'Batna', 2, '2006-02-15 09:45:25'),
(59, 'Baybay', 73, '2006-02-15 09:45:25'),
(60, 'Bayugan', 73, '2006-02-15 09:45:25'),
(61, 'Yangon', 62, '2006-02-15 10:45:25'),
(62, 'Austin', 101, '2006-02-15 11:45:25');

--
-- Data for Name: address; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO address (address_id, address, address2, district, city_id, postal_code, phone, last_update) VALUES
(1, '47 MySakila Drive', NULL, 'Alberta', 20, '', '403-1234567', '2006-02-15 09:45:30'),
(2, '28 MySQL Boulevard', NULL, 'QLD', 8, '', '323-9876543', '2006-02-15 09:45:30'),
(3, '23 Workhaven Lane', NULL, 'Alberta', 20, '', '14033335568', '2006-02-15 09:45:30'),
(4, '1411 Lillydale Drive', NULL, 'QLD', 8, '', '6172235589', '2006-02-15 09:45:30'),
(5, '1913 Hanoi Way', '', 'Nagasaki', 10, '35200', '28303384290', '2006-02-15 09:45:30'),
(6, '1121 Loja Avenue', '', 'California', 11, '17886', '838635286649', '2006-02-15 09:45:30'),
(7, '692 Joliet Street', '', 'Attika', 39, '83579', '448477190408', '2006-02-15 09:45:30'),
(8, '1566 Inegl Manor', '', 'Mandalay', 61, '53561', '705814003527', '2006-02-15 09:45:30'),
(9, '53 Idfu Parkway', '', 'Nantou', 33, '42399', '10655648674', '2006-02-15 09:45:30'),
(10, '1795 Santiago de Compostela Way', '', 'Texas', 62, '18743', '860452626434', '2006-02-15 09:45:30');

--
-- Data for Name: category; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO category (category_id, name, last_update) VALUES
(1, 'Action', '2006-02-15 09:46:27'),
(2, 'Animation', '2006-02-15 09:46:27'),
(3, 'Children', '2006-02-15 09:46:27'),
(4, 'Classics', '2006-02-15 09:46:27'),
(5, 'Comedy', '2006-02-15 09:46:27'),
(6, 'Documentary', '2006-02-15 09:46:27'),
(7, 'Drama', '2006-02-15 09:46:27'),
(8, 'Family', '2006-02-15 09:46:27'),
(9, 'Foreign', '2006-02-15 09:46:27'),
(10, 'Games', '2006-02-15 09:46:27'),
(11, 'Horror', '2006-02-15 09:46:27'),
(12, 'Music', '2006-02-15 09:46:27'),
(13, 'New', '2006-02-15 09:46:27'),
(14, 'Sci-Fi', '2006-02-15 09:46:27'),
(15, 'Sports', '2006-02-15 09:46:27'),
(16, 'Travel', '2006-02-15 09:46:27');

--
-- Data for Name: actor; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- INSERT INTO actor (actor_id, first_name, last_name, last_update) VALUES
-- (1, 'PENELOPE', 'GUINESS', '2006-02-15 09:34:33'),
-- (2, 'NICK', 'WAHLBERG', '2006-02-15 09:34:33'),
-- (3, 'ED', 'CHASE', '2006-02-15 09:34:33'),
-- (4, 'JENNIFER', 'DAVIS', '2006-02-15 09:34:33'),
-- (5, 'JOHNNY', 'LOLLOBRIGIDA', '2006-02-15 09:34:33'),
-- (6, 'BETTE', 'NICHOLSON', '2006-02-15 09:34:33'),
-- (7, 'GRACE', 'MOSTEL', '2006-02-15 09:34:33'),
-- (8, 'MATTHEW', 'JOHANSSON', '2006-02-15 09:34:33'),
-- (9, 'JOE', 'SWANK', '2006-02-15 09:34:33'),
-- (10, 'CHRISTIAN', 'GABLE', '2006-02-15 09:34:33'),
-- (11, 'ZERO', 'CAGE', '2006-02-15 09:34:33'),
-- (12, 'KARL', 'BERRY', '2006-02-15 09:34:33'),
-- (13, 'UMA', 'WOOD', '2006-02-15 09:34:33'),
-- (14, 'VIVIEN', 'BERGEN', '2006-02-15 09:34:33'),
-- (15, 'CUBA', 'OLIVIER', '2006-02-15 09:34:33'),
-- (16, 'FRED', 'COSTNER', '2006-02-15 09:34:33'),
-- (17, 'HELEN', 'VOIGHT', '2006-02-15 09:34:33'),
-- (18, 'DAN', 'TORN', '2006-02-15 09:34:33'),
-- (19, 'BOB', 'FAWCETT', '2006-02-15 09:34:33'),
-- (20, 'LUCILLE', 'TRACY', '2006-02-15 09:34:33'),
-- (21, 'KIRSTEN', 'PALTROW', '2006-02-15 09:34:33'),
-- (22, 'ELVIS', 'MARX', '2006-02-15 09:34:33'),
-- (23, 'SANDRA', 'KILMER', '2006-02-15 09:34:33'),
-- (24, 'CAMERON', 'STREEP', '2006-02-15 09:34:33'),
-- (25, 'KEVIN', 'BLOOM', '2006-02-15 09:34:33'),
-- (26, 'RIP', 'CRAWFORD', '2006-02-15 09:34:33'),
-- (27, 'JULIA', 'MCQUEEN', '2006-02-15 09:34:33'),
-- (28, 'WOODY', 'HOFFMAN', '2006-02-15 09:34:33'),
-- (29, 'ALEC', 'WAYNE', '2006-02-15 09:34:33'),
-- (30, 'SANDRA', 'PECK', '2006-02-15 09:34:33');

--
-- Data for Name: film; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO film (film_id, title, description, release_year, language_id, rental_duration, rental_rate, length, replacement_cost, rating, last_update, special_features, streaming_available) VALUES
(1, 'ACADEMY DINOSAUR', 'A Epic Drama of a Feminist And a Mad Scientist who must Battle a Teacher in The Canadian Rockies', 2006, 1, 6, 0.99, 86, 20.99, 'PG', '2006-02-15 10:03:42', '{Deleted Scenes,Behind the Scenes}', false),
(2, 'ACE GOLDFINGER', 'A Astounding Epistle of a Database Administrator And a Explorer who must Find a Car in Ancient China', 2006, 1, 3, 4.99, 48, 12.99, 'G', '2006-02-15 10:03:42', '{Trailers,Deleted Scenes}', false),
(3, 'ADAPTATION HOLES', 'A Astounding Reflection of a Lumberjack And a Car who must Sink a Lumberjack in A Baloon Factory', 2006, 1, 7, 2.99, 50, 18.99, 'NC-17', '2006-02-15 10:03:42', '{Trailers,Deleted Scenes}', true),
(4, 'AFFAIR PREJUDICE', 'A Fanciful Documentary of a Frisbee And a Lumberjack who must Chase a Monkey in A Shark Tank', 2006, 1, 5, 2.99, 117, 26.99, 'G', '2006-02-15 10:03:42', '{Commentaries,Behind the Scenes}', true),
(5, 'AFRICAN EGG', 'A Fast-Paced Documentary of a Pastry Chef And a Dentist who must Pursue a Forensic Psychologist in The Gulf of Mexico', 2006, 1, 6, 2.99, 130, 22.99, 'G', '2006-02-15 10:03:42', '{Deleted Scenes}', true),
(6, 'AGENT TRUMAN', 'A Intrepid Panorama of a Robot And a Boy who must Escape a Sumo Wrestler in Ancient China', 2006, 1, 3, 2.99, 169, 17.99, 'PG', '2006-02-15 10:03:42', '{Deleted Scenes}', true),
(7, 'AIRPLANE SIERRA', 'A Touching Saga of a Hunter And a Butler who must Discover a Butler in A Jet Boat', 2006, 1, 6, 4.99, 62, 28.99, 'PG-13', '2006-02-15 10:03:42', '{Trailers,Deleted Scenes}', true),
(8, 'AIRPORT POLLOCK', 'A Epic Tale of a Moose And a Girl who must Confront a Monkey in Ancient India', 2006, 1, 6, 4.99, 54, 15.99, 'R', '2006-02-15 10:03:42', '{Trailers}', true),
(9, 'ALABAMA DEVIL', 'A Thoughtful Panorama of a Database Administrator And a Mad Scientist who must Outgun a Mad Scientist in A Jet Boat', 2006, 1, 3, 2.99, 114, 21.99, 'PG-13', '2006-02-15 10:03:42', '{Trailers,Deleted Scenes}', false),
(10, 'ALADDIN CALENDAR', 'A Action-Packed Tale of a Man And a Lumberjack who must Reach a Feminist in Ancient China', 2006, 1, 6, 4.99, 63, 24.99, 'NC-17', '2006-02-15 10:03:42', '{Trailers,Deleted Scenes}', false),
(11, 'ALAMO VIDEOTAPE', 'A Boring Epistle of a Butler And a Cat who must Fight a Pastry Chef in A MySQL Convention', 2006, 1, 6, 0.99, 126, 16.99, 'G', '2006-02-15 10:03:42', '{Commentaries,Behind the Scenes}', false),
(12, 'ALASKA PHANTOM', 'A Fanciful Saga of a Hunter And a Pastry Chef who must Vanquish a Boy in Australia', 2006, 1, 6, 0.99, 136, 22.99, 'PG', '2006-02-15 10:03:42', '{Commentaries,Deleted Scenes}', true),
(13, 'ALI FOREVER', 'A Action-Packed Drama of a Dentist And a Crocodile who must Battle a Feminist in The Canadian Rockies', 2006, 1, 4, 4.99, 150, 21.99, 'PG', '2006-02-15 10:03:42', '{Deleted Scenes,Behind the Scenes}', false),
(14, 'ALICE FANTASIA', 'A Emotional Drama of a A Shark And a Database Administrator who must Vanquish a Pioneer in Soviet Georgia', 2006, 1, 6, 0.99, 94, 23.99, 'NC-17', '2006-02-15 10:03:42', '{Trailers,Deleted Scenes,Behind the Scenes}', true),
(15, 'ALIEN CENTER', 'A Brilliant Drama of a Cat And a Mad Scientist who must Battle a Feminist in A MySQL Convention', 2006, 1, 5, 2.99, 46, 10.99, 'NC-17', '2006-02-15 10:03:42', '{Trailers,Commentaries,Behind the Scenes}', false),
(16, 'AMADEUS HOLY', 'A Emotional Display of a Pioneer And a Technical Writer who must Battle a Man in A Baloon Factory', 2006, 1, 6, 0.99, 113, 20.99, 'PG', '2006-02-15 10:03:42', '{Commentaries,Deleted Scenes,Behind the Scenes}', true),
(17, 'AMERICAN CIRCUS', 'A Insightful Drama of a Girl And a Astronaut who must Face a Database Administrator in A Shark Tank', 2006, 1, 3, 4.99, 129, 17.99, 'R', '2006-02-15 10:03:42', '{Commentaries,Behind the Scenes}', false),
(18, 'ANTHEM LUKE', 'A Touching Panorama of a Waitress And a Woman who must Outrace a Dog in An Abandoned Amusement Park', 2006, 1, 5, 4.99, 91, 16.99, 'PG-13', '2006-02-15 10:03:42', '{Deleted Scenes,Behind the Scenes}', true),
(19, 'APOCALYPSE FLAMINGOS', 'A Astounding Story of a Dog And a Squirrel who must Defeat a Woman in An Abandoned Amusement Park', 2006, 1, 6, 0.99, 119, 11.99, 'R', '2006-02-15 10:03:42', '{Trailers,Commentaries}', false),
(20, 'ARMY FLINTSTONES', 'A Boring Saga of a Database Administrator And a Womanizer who must Battle a Waitress in Nigeria', 2006, 1, 4, 0.99, 148, 22.99, 'R', '2006-02-15 10:03:42', '{Trailers,Commentaries}', false);

--
-- Data for Name: film_actor; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- INSERT INTO film_actor (actor_id, film_id, last_update) VALUES
-- (1, 1, '2006-02-15 10:05:03'),
-- (10, 1, '2006-02-15 10:05:03'),
-- (20, 1, '2006-02-15 10:05:03'),
-- (30, 1, '2006-02-15 10:05:03'),
-- (2, 2, '2006-02-15 10:05:03'),
-- (11, 2, '2006-02-15 10:05:03'),
-- (21, 2, '2006-02-15 10:05:03'),
-- (3, 3, '2006-02-15 10:05:03'),
-- (12, 3, '2006-02-15 10:05:03'),
-- (22, 3, '2006-02-15 10:05:03'),
-- (4, 4, '2006-02-15 10:05:03'),
-- (13, 4, '2006-02-15 10:05:03'),
-- (23, 4, '2006-02-15 10:05:03'),
-- (5, 5, '2006-02-15 10:05:03'),
-- (14, 5, '2006-02-15 10:05:03'),
-- (24, 5, '2006-02-15 10:05:03'),
-- (6, 6, '2006-02-15 10:05:03'),
-- (15, 6, '2006-02-15 10:05:03'),
-- (25, 6, '2006-02-15 10:05:03'),
-- (7, 7, '2006-02-15 10:05:03'),
-- (16, 7, '2006-02-15 10:05:03'),
-- (26, 7, '2006-02-15 10:05:03'),
-- (8, 8, '2006-02-15 10:05:03'),
-- (17, 8, '2006-02-15 10:05:03'),
-- (27, 8, '2006-02-15 10:05:03'),
-- (9, 9, '2006-02-15 10:05:03'),
-- (18, 9, '2006-02-15 10:05:03'),
-- (28, 9, '2006-02-15 10:05:03'),
-- (10, 10, '2006-02-15 10:05:03'),
-- (19, 10, '2006-02-15 10:05:03'),
-- (29, 10, '2006-02-15 10:05:03'),
-- (1, 11, '2006-02-15 10:05:03'),
-- (11, 11, '2006-02-15 10:05:03'),
-- (30, 11, '2006-02-15 10:05:03'),
-- (2, 12, '2006-02-15 10:05:03'),
-- (12, 12, '2006-02-15 10:05:03'),
-- (21, 12, '2006-02-15 10:05:03'),
-- (3, 13, '2006-02-15 10:05:03'),
-- (13, 13, '2006-02-15 10:05:03'),
-- (22, 13, '2006-02-15 10:05:03'),
-- (4, 14, '2006-02-15 10:05:03'),
-- (14, 14, '2006-02-15 10:05:03'),
-- (23, 14, '2006-02-15 10:05:03'),
-- (5, 15, '2006-02-15 10:05:03'),
-- (15, 15, '2006-02-15 10:05:03'),
-- (24, 15, '2006-02-15 10:05:03'),
-- (6, 16, '2006-02-15 10:05:03'),
-- (16, 16, '2006-02-15 10:05:03'),
-- (7, 17, '2006-02-15 10:05:03'),
-- (17, 17, '2006-02-15 10:05:03'),
-- (8, 18, '2006-02-15 10:05:03'),
-- (18, 18, '2006-02-15 10:05:03'),
-- (9, 19, '2006-02-15 10:05:03'),
-- (19, 19, '2006-02-15 10:05:03'),
-- (10, 20, '2006-02-15 10:05:03'),
-- (20, 20, '2006-02-15 10:05:03');

--
-- Data for Name: film_category; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO film_category (film_id, category_id, last_update) VALUES
(1, 6, '2006-02-15 10:07:09'),
(2, 11, '2006-02-15 10:07:09'),
(3, 6, '2006-02-15 10:07:09'),
(4, 11, '2006-02-15 10:07:09'),
(5, 8, '2006-02-15 10:07:09'),
(6, 9, '2006-02-15 10:07:09'),
(7, 5, '2006-02-15 10:07:09'),
(8, 11, '2006-02-15 10:07:09'),
(9, 11, '2006-02-15 10:07:09'),
(10, 15, '2006-02-15 10:07:09'),
(11, 2, '2006-02-15 10:07:09'),
(12, 9, '2006-02-15 10:07:09'),
(13, 7, '2006-02-15 10:07:09'),
(14, 2, '2006-02-15 10:07:09'),
(15, 14, '2006-02-15 10:07:09'),
(16, 7, '2006-02-15 10:07:09'),
(17, 7, '2006-02-15 10:07:09'),
(18, 5, '2006-02-15 10:07:09'),
(19, 1, '2006-02-15 10:07:09'),
(20, 1, '2006-02-15 10:07:09');

--
-- Data for Name: staff; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO staff (staff_id, first_name, last_name, address_id, email, store_id, active, username, password, last_update, picture) VALUES
(1, 'Mike', 'Hillyer', 3, 'Mike.Hillyer@sakilastaff.com', 1, true, 'Mike', '8cb2237d0679ca88db6464eac60da96345513964', '2006-05-16 16:13:11.79328', NULL),
(2, 'Jon', 'Stephens', 4, 'Jon.Stephens@sakilastaff.com', 2, true, 'Jon', '8cb2237d0679ca88db6464eac60da96345513964', '2006-05-16 16:13:11.79328', NULL);

--
-- Data for Name: store; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO store (store_id, manager_staff_id, address_id, last_update) VALUES
(1, 1, 1, '2006-02-15 09:57:12'),
(2, 2, 2, '2006-02-15 09:57:12');

--
-- Data for Name: customer; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO customer (customer_id, store_id, first_name, last_name, email, address_id, activebool, create_date, last_update, active) VALUES
(1, 1, 'MARY', 'SMITH', 'MARY.SMITH@sakilacustomer.org', 5, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(2, 1, 'PATRICIA', 'JOHNSON', 'PATRICIA.JOHNSON@sakilacustomer.org', 6, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(3, 1, 'LINDA', 'WILLIAMS', 'LINDA.WILLIAMS@sakilacustomer.org', 7, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(4, 2, 'BARBARA', 'JONES', 'BARBARA.JONES@sakilacustomer.org', 8, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(5, 1, 'ELIZABETH', 'BROWN', 'ELIZABETH.BROWN@sakilacustomer.org', 9, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(6, 2, 'JENNIFER', 'DAVIS', 'JENNIFER.DAVIS@sakilacustomer.org', 10, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(7, 1, 'MARIA', 'MILLER', 'MARIA.MILLER@sakilacustomer.org', 5, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(8, 2, 'SUSAN', 'WILSON', 'SUSAN.WILSON@sakilacustomer.org', 6, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(9, 2, 'MARGARET', 'MOORE', 'MARGARET.MOORE@sakilacustomer.org', 7, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(10, 1, 'DOROTHY', 'TAYLOR', 'DOROTHY.TAYLOR@sakilacustomer.org', 8, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(11, 1, 'HELEN', 'HARRIS', 'HELEN.HARRIS@sakilacustomer.org', 5, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(12, 2, 'NANCY', 'MARTIN', 'NANCY.MARTIN@sakilacustomer.org', 6, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(13, 1, 'BETTY', 'GARCIA', 'BETTY.GARCIA@sakilacustomer.org', 7, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(14, 2, 'SANDRA', 'RODRIGUEZ', 'SANDRA.RODRIGUEZ@sakilacustomer.org', 8, true, '2006-02-14', '2006-02-15 09:57:20', 1),
(15, 1, 'DONNA', 'LEWIS', 'DONNA.LEWIS@sakilacustomer.org', 9, true, '2006-02-14', '2006-02-15 09:57:20', 1);

--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO inventory (inventory_id, film_id, store_id, last_update) VALUES
(1, 1, 1, '2006-02-15 10:09:17'),
(2, 1, 1, '2006-02-15 10:09:17'),
(3, 1, 1, '2006-02-15 10:09:17'),
(4, 1, 1, '2006-02-15 10:09:17'),
(5, 1, 2, '2006-02-15 10:09:17'),
(6, 1, 2, '2006-02-15 10:09:17'),
(7, 1, 2, '2006-02-15 10:09:17'),
(8, 1, 2, '2006-02-15 10:09:17'),
(9, 2, 1, '2006-02-15 10:09:17'),
(10, 2, 1, '2006-02-15 10:09:17'),
(11, 2, 1, '2006-02-15 10:09:17'),
(12, 2, 2, '2006-02-15 10:09:17'),
(13, 2, 2, '2006-02-15 10:09:17'),
(14, 2, 2, '2006-02-15 10:09:17'),
(15, 3, 1, '2006-02-15 10:09:17'),
(16, 3, 1, '2006-02-15 10:09:17'),
(17, 3, 1, '2006-02-15 10:09:17'),
(18, 3, 2, '2006-02-15 10:09:17'),
(19, 3, 2, '2006-02-15 10:09:17'),
(20, 3, 2, '2006-02-15 10:09:17'),
(21, 4, 1, '2006-02-15 10:09:17'),
(22, 4, 1, '2006-02-15 10:09:17'),
(23, 4, 1, '2006-02-15 10:09:17'),
(24, 4, 2, '2006-02-15 10:09:17'),
(25, 4, 2, '2006-02-15 10:09:17'),
(26, 4, 2, '2006-02-15 10:09:17'),
(27, 5, 1, '2006-02-15 10:09:17'),
(28, 5, 1, '2006-02-15 10:09:17'),
(29, 5, 1, '2006-02-15 10:09:17'),
(30, 5, 2, '2006-02-15 10:09:17'),
(31, 6, 1, '2006-02-15 10:09:17'),
(32, 6, 1, '2006-02-15 10:09:17'),
(33, 6, 2, '2006-02-15 10:09:17'),
(34, 7, 1, '2006-02-15 10:09:17'),
(35, 7, 2, '2006-02-15 10:09:17'),
(36, 8, 1, '2006-02-15 10:09:17'),
(37, 8, 2, '2006-02-15 10:09:17'),
(38, 9, 1, '2006-02-15 10:09:17'),
(39, 9, 2, '2006-02-15 10:09:17'),
(40, 10, 1, '2006-02-15 10:09:17');

--
-- Data for Name: rental; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO rental (rental_id, rental_date, inventory_id, customer_id, return_date, staff_id, last_update) VALUES
(1, '2005-05-24 22:53:30', 1, 2, '2005-05-26 22:04:30', 1, '2006-02-15 21:30:53'),
(2, '2005-05-24 22:54:33', 2, 4, '2005-05-28 19:40:33', 1, '2006-02-15 21:30:53'),
(3, '2005-05-24 23:03:39', 3, 4, '2005-06-01 22:12:39', 1, '2006-02-15 21:30:53'),
(4, '2005-05-24 23:04:41', 4, 2, '2005-06-03 01:43:41', 2, '2006-02-15 21:30:53'),
(5, '2005-05-24 23:05:21', 5, 2, '2005-06-02 04:33:21', 1, '2006-02-15 21:30:53'),
(6, '2005-05-24 23:08:07', 6, 5, '2005-05-27 01:32:07', 1, '2006-02-15 21:30:53'),
(7, '2005-05-24 23:11:53', 7, 2, '2005-05-29 20:34:53', 2, '2006-02-15 21:30:53'),
(8, '2005-05-24 23:31:46', 8, 9, '2005-05-27 23:33:46', 2, '2006-02-15 21:30:53'),
(9, '2005-05-25 00:00:40', 9, 12, '2005-05-28 00:22:40', 1, '2006-02-15 21:30:53'),
(10, '2005-05-25 00:02:21', 10, 9, '2005-05-31 22:44:21', 2, '2006-02-15 21:30:53'),
(11, '2005-05-25 00:09:02', 11, 14, NULL, 2, '2006-02-15 21:30:53'),
(12, '2005-05-25 00:22:55', 12, 18, '2005-05-30 05:44:55', 2, '2006-02-15 21:30:53'),
(13, '2005-05-25 00:31:15', 13, 13, '2005-05-30 06:15:15', 1, '2006-02-15 21:30:53'),
(14, '2005-05-25 00:39:22', 14, 4, '2005-05-25 06:51:22', 1, '2006-02-15 21:30:53'),
(15, '2005-05-25 00:43:11', 15, 3, '2005-05-29 06:35:11', 1, '2006-02-15 21:30:53');

--
-- Data for Name: payment; Type: TABLE DATA; Schema: public; Owner: postgres
--

-- INSERT INTO payment (payment_id, customer_id, staff_id, rental_id, amount, payment_date) VALUES
-- (1, 130, 1, 1, 5.99, '2005-05-25 11:30:37'),
-- (2, 459, 1, 2, 9.99, '2005-05-25 11:30:37'),
-- (3, 408, 1, 3, 5.99, '2005-05-25 11:30:37'),
-- (4, 333, 2, 4, 9.99, '2005-05-25 11:30:37'),
-- (5, 222, 1, 5, 1.99, '2005-05-25 11:30:37'),
-- (6, 549, 1, 6, 7.99, '2005-05-25 11:30:37'),
-- (7, 269, 2, 7, 7.99, '2005-05-25 11:30:37'),
-- (8, 239, 2, 8, 2.99, '2005-05-25 11:30:37'),
-- (9, 126, 1, 9, 0.99, '2005-05-25 11:30:37'),
-- (10, 399, 2, 10, 5.99, '2005-05-25 11:30:37'),
-- (11, 142, 2, 11, 0.99, '2005-05-25 11:30:37'),
-- (12, 261, 2, 12, 2.99, '2005-05-25 11:30:37'),
-- (13, 334, 1, 13, 8.99, '2005-05-25 11:30:37'),
-- (14, 446, 1, 14, 4.99, '2005-05-25 11:30:37'),
-- (15, 319, 1, 15, 4.99, '2005-05-25 11:30:37');

-- streaming_subscription data will be added in Migration #3

-- --
-- -- Name: actor_actor_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('actor_actor_id_seq', 30, true);

-- --
-- -- Name: address_address_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('address_address_id_seq', 10, true);

-- --
-- -- Name: category_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('category_category_id_seq', 16, true);

-- --
-- -- Name: city_city_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('city_city_id_seq', 60, true);

-- --
-- -- Name: country_country_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('country_country_id_seq', (SELECT MAX(country_id) FROM country), true);

-- --
-- -- Name: customer_customer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('customer_customer_id_seq', 10, true);

-- --
-- -- Name: film_film_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('film_film_id_seq', 15, true);

-- --
-- -- Name: inventory_inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('inventory_inventory_id_seq', 30, true);

-- --
-- -- Name: language_language_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('language_language_id_seq', 6, true);

-- --
-- -- Name: payment_payment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('payment_payment_id_seq', 15, true);

-- --
-- -- Name: rental_rental_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('rental_rental_id_seq', 15, true);

-- --
-- -- Name: staff_staff_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('staff_staff_id_seq', 2, true);

-- --
-- -- Name: store_store_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- SELECT pg_catalog.setval('store_store_id_seq', 2, true);

-- --
-- -- Name: streaming_subscription_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
-- --

-- streaming_subscription_id_seq will be added in Migration #3

--
-- PostgreSQL database dump complete
--

-- Reset sequences to current max values
SELECT pg_catalog.setval('address_address_id_seq', (SELECT MAX(address_id) FROM address), true);
SELECT pg_catalog.setval('category_category_id_seq', (SELECT MAX(category_id) FROM category), true);
SELECT pg_catalog.setval('city_city_id_seq', (SELECT MAX(city_id) FROM city), true);
SELECT pg_catalog.setval('country_country_id_seq', (SELECT MAX(country_id) FROM country), true);
SELECT pg_catalog.setval('customer_customer_id_seq', (SELECT MAX(customer_id) FROM customer), true);
SELECT pg_catalog.setval('film_film_id_seq', (SELECT MAX(film_id) FROM film), true);
SELECT pg_catalog.setval('inventory_inventory_id_seq', (SELECT MAX(inventory_id) FROM inventory), true);
SELECT pg_catalog.setval('language_language_id_seq', (SELECT MAX(language_id) FROM language), true);
SELECT pg_catalog.setval('rental_rental_id_seq', (SELECT MAX(rental_id) FROM rental), true);
SELECT pg_catalog.setval('staff_staff_id_seq', (SELECT MAX(staff_id) FROM staff), true);
SELECT pg_catalog.setval('store_store_id_seq', (SELECT MAX(store_id) FROM store), true);
-- streaming_subscription_id_seq will be added in Migration #3

-- Re-enable foreign key checks
SET session_replication_role = DEFAULT;

COMMIT;
