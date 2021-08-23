customer_type = (
    ('103', 'Corporate'),
    ('104', 'Individual'),
)
DEFAULT_INSURANCE_TYPE = '104'  # Individual

payment_types = (
    ('CC', 'Credit Customer'),
    ('OT', 'Others(Receipt Voucher)'),
)

vehicle_usages = (
    ('10100', 'Private'),
    ('10101', 'Commercial'),
)

vehicle_types = (
    ('1001', 'PRIVATE TYPE'),
    ('1002', 'GOODS CARRYING'),
    ('1003', 'PASSENGER CARRYING'),
    ('1004', 'MISCELLANEOUS'),
)

vehicle_body_types = (
    ('2', 'COUPE'),
    ('20', 'MPV'),
    ('6', 'SEDAN'),
    ('7', 'STATION WAGON'),
    ('8', 'SUV'),
    ('36', 'HATCHBACK'),
    ('49', 'PICK UP'),
    ('82', 'SUV COUPE'),
    ('79', 'CONVERTIBLE'),
    ('38', 'HARD TOP'),
    ('83', 'CROSSOVER'),
)

emirate_mapping = {
    'DU': '10',  # Dubai
    'AD': '20',  # Abu Dhabi
    'SJ': '30',  # Sharjah
    'AJ': '40',  # Ajman
    'UQ': '50',  # Umm Al-Quwain
    'RK': '60',  # Ras Al-Khaimah
    'FJ': '70',  # Fujairah
}

vehicle_makes_our_id_to_dat_id = dict((
    (52, '001'),  # ALFA ROMEO => Alfa Romeo
    (42, '002'),  # ASTON MARTIN => Aston Martin
    (1, '003'),  # AUDI => Audi
    (2, '004'),  # BENTLEY => Bentley
    (4, '006'),  # CADILLAC => Cadillac
    (5, '007'),  # CHEVROLET => Chevrolet
    (45, '008'),  # CHRYSLER => Chrysler
    (46, '009'),  # DAIHATSU => Daihatsu
    (6, '010'),  # DODGE => Dodge
    (32, '010'),  # RAM => Dodge
    (7, '011'),  # FERRARI => Ferrari
    (9, '012'),  # FORD => Ford
    (11, '013'),  # GMC => GMC
    (12, '014'),  # HONDA => Honda
    (71, '015'),  # HUMMER => Hummer
    (13, '016'),  # HYUNDAI => Hyundai
    (14, '017'),  # INFINITI => Infiniti
    (16, '018'),  # JAGUAR => Jaguar
    (17, '019'),  # JEEP => Jeep
    (18, '020'),  # KIA => Kia
    (19, '021'),  # LAND ROVER => Land Rover
    (20, '022'),  # LEXUS => Lexus
    (21, '023'),  # LINCOLN => Lincoln
    (22, '024'),  # MASERATI => Maserati
    (67, '025'),  # MAYBACH => Maybach
    (23, '026'),  # MAZDA => Mazda
    (72, '028'),  # MERCURY => Mercury
    (26, '029'),  # MINI => MINI
    (27, '030'),  # MITSUBISHI => Mitsubishi
    (28, '031'),  # NISSAN => Nissan
    (30, '032'),  # PEUGEOT => Peugeot
    (31, '033'),  # PORSCHE => Porsche
    (33, '034'),  # RENAULT => Renault
    (69, '036'),  # SAAB => Saab
    (63, '037'),  # SEAT => SEAT
    (51, '039'),  # SSANGYONG => Ssangyong
    (36, '040'),  # SUBARU => Subaru
    (37, '041'),  # SUZUKI => Suzuki
    (39, '042'),  # TOYOTA => Toyota
    (40, '043'),  # VOLKSWAGEN => Volkswagen
    (41, '044'),  # VOLVO => Volvo
    (8, '056'),  # FIAT => Fiat
    (56, '059'),  # ISUZU => Isuzu
    (29, '070'),  # OPEL => Opel
    (10, '071'),  # GEELY => Geely
    (44, '139'),  # CHERY => Chery
    (68, '143'),  # CMC => CMC
    (48, '219'),  # LAMBORGHINI => Lamborghini
    (49, '229'),  # LOTUS => Lotus
    (62, '270'),  # PROTON => Proton
    (66, '344'),  # GREAT WALL => Great Wall
    (57, '344'),  # LUXGEN => Luxgen
    (43, '344'),  # CHANGAN => Changan
    (50, '408'),  # MG => MG
    (53, '536'),  # BAIC => Baic
    (15, '595'),  # JAC => JAC
    (60, '595'),  # BRILLIANCE => Brilliance
    (38, '596'),  # TESLA => Tesla
    (65, '596'),  # FISKER => Fisker
    (24, '596'),  # MCLAREN => McLaren
    (61, '596'),  # BUGATTI => Bugatti
    (70, '596'),  # BYD => BYD
    (55, '596'),  # GAC => GAC
    (3, '005'),  # B.M.W -> BMW
    (25, '027'),  # MERCEDES BENZ -> Mercedes-Benz
    (34, '035'),  # ROLLS ROYCE -> Rolls-Royce
    (35, '038'),  # SKODA -> Škoda
    (54, '552'),  # CITROEN -> Citroën

    # We don't have a separate Range Rover make. Instead we have Land Rover, which is mapped in the list above
    # (19, '045'),  # RANGE ROVER -> Land Rover

    # No mapping found for these brands. Most of them are heavy duty vehicles, or bikes

    # (None, '046'),  # CATERPILLAR ->
    # (None, '047'),  # MAN ->
    # (None, '048'),  # BOBCAT ->
    # (None, '049'),  # ASHOK LEYLAND ->
    # (None, '050'),  # BEDFORD ->
    # (None, '051'),  # HARLEY DAVIDSON ->
    # (None, '052'),  # KOMATSU ->
    # (None, '053'),  # CASE ->
    # (None, '054'),  # DAEWOO ->
    # (None, '055'),  # ESCANIA ->
    # (None, '057'),  # HINO ->
    # (None, '058'),  # HITACHI ->
    # (None, '060'),  # JCB ->
    # (None, '061'),  # KATO ->
    # (None, '062'),  # KING LONG ->
    # (None, '063'),  # KLEMM ->
    # (None, '064'),  # LIEBHERR ->
    # (None, '065'),  # SKID ->
    # (None, '067'),  # FOTON ->
    # (None, '068'),  # BOMAG ->
    # (None, '069'),  # DUCATI ->
    # (None, '185'),  # HIGER ->
    # (None, '199'),  # BORGWARD ->
    # (None, '205'),  # JMC ->
    # (None, '208'),  # KAWASAKI ->
    # (None, '233'),  # MAHINDRA ->
    # (None, '265'),  # PONTIAC ->
    # (None, '285'),  # SCANIA ->
    # (None, '294'),  # SMART ->
    # (None, '301'),  # TADANO ->
    # (None, '303'),  # TATA ->
    # (None, '312'),  # TVS ->
    # (None, '326'),  # YAMAHA ->
    # (None, '400'),  # ACURA ->
    # (None, '406'),  # JINBEI ->
    # (None, '595'),  # BUICK ->
    # (None, '596'),  # PAGANI ->
    # (None, '596'),  # KOENIGSEGG ->
    # (None, '066'),  # UD ->
    # (None, '596'),  # ROVER ->
))

vehicle_makes = (
    ('001', 'ALFA ROMEO'),
    ('002', 'ASTON MARTIN'),
    ('003', 'AUDI'),
    ('004', 'BENTLEY'),
    ('005', 'B.M.W'),
    ('006', 'CADILLAC'),
    ('007', 'CHEVROLET'),
    ('008', 'CHRYSLER'),
    ('009', 'DAIHATSU'),
    ('010', 'DODGE'),
    ('011', 'FERRARI'),
    ('012', 'FORD'),
    ('013', 'GMC'),
    ('014', 'HONDA'),
    ('015', 'HUMMER'),
    ('016', 'HYUNDAI'),
    ('017', 'INFINITI'),
    ('018', 'JAGUAR'),
    ('019', 'JEEP'),
    ('020', 'KIA'),
    ('021', 'LAND ROVER'),
    ('022', 'LEXUS'),
    ('023', 'LINCOLN'),
    ('024', 'MASERATI'),
    ('025', 'MAYBACH'),
    ('026', 'MAZDA'),
    ('027', 'MERCEDES BENZ'),
    ('028', 'MERCURY'),
    ('029', 'MINI'),
    ('030', 'MITSUBISHI'),
    ('031', 'NISSAN'),
    ('032', 'PEUGEOT'),
    ('033', 'PORSCHE'),
    ('034', 'RENAULT'),
    ('035', 'ROLLS ROYCE'),
    ('036', 'SAAB'),
    ('037', 'SEAT'),
    ('038', 'SKODA'),
    ('039', 'SSANGYONG'),
    ('040', 'SUBARU'),
    ('041', 'SUZUKI'),
    ('042', 'TOYOTA'),
    ('043', 'VOLKSWAGEN'),
    ('044', 'VOLVO'),
    ('045', 'RANGE ROVER'),
    ('046', 'CATERPILLAR'),
    ('047', 'MAN'),
    ('048', 'BOBCAT'),
    ('049', 'ASHOK LEYLAND'),
    ('050', 'BEDFORD'),
    ('051', 'HARLEY DAVIDSON'),
    ('052', 'KOMATSU'),
    ('053', 'CASE'),
    ('054', 'DAEWOO'),
    ('055', 'ESCANIA'),
    ('056', 'FIAT'),
    ('057', 'HINO'),
    ('058', 'HITACHI'),
    ('059', 'ISUZU'),
    ('060', 'JCB'),
    ('061', 'KATO'),
    ('062', 'KING LONG'),
    ('063', 'KLEMM'),
    ('064', 'LIEBHERR'),
    ('065', 'SKID'),
    ('066', 'UD'),
    ('067', 'FOTON'),
    ('068', 'BOMAG'),
    ('069', 'DUCATI'),
    ('070', 'OPEL'),
    ('071', 'GEELY'),
    ('139', 'CHERY'),
    ('143', 'CMC'),
    ('185', 'HIGER'),
    ('199', 'BORGWARD'),
    ('205', 'JMC'),
    ('208', 'KAWASAKI'),
    ('219', 'LAMBORGHINI'),
    ('229', 'LOTUS'),
    ('233', 'MAHINDRA'),
    ('265', 'PONTIAC'),
    ('270', 'PROTON'),
    ('285', 'SCANIA'),
    ('294', 'SMART'),
    ('301', 'TADANO'),
    ('303', 'TATA'),
    ('312', 'TVS'),
    ('326', 'YAMAHA'),
    ('344', 'GREAT WALL'),
    ('344', 'LUXGEN'),
    ('344', 'CHANGAN'),
    ('400', 'ACURA'),
    ('406', 'JINBEI'),
    ('408', 'MG'),
    ('536', 'BAIC'),
    ('552', 'CITROEN'),
    ('595', 'JAC'),
    ('595', 'BRILLIANCE'),
    ('595', 'BUICK'),
    ('596', 'TESLA'),
    ('596', 'ROVER'),
    ('596', 'FISKER'),
    ('596', 'PAGANI'),
    ('596', 'MCLAREN'),
    ('596', 'KOENIGSEGG'),
    ('596', 'BUGATTI'),
    ('596', 'BYD'),
    ('596', 'GAC'),
)