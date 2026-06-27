from urllib.parse import quote

from app.models.schemas import Question, QuestionAudio


def make_svg_data_uri(title: str, subtitle: str, background: str, accent: str) -> str:
    safe_subtitle = subtitle[:72]
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="640" height="420" viewBox="0 0 640 420">
    <rect width="640" height="420" fill="{background}"/>
    <circle cx="520" cy="80" r="46" fill="{accent}" opacity="0.35"/>
    <rect x="70" y="255" width="500" height="72" rx="18" fill="#ffffff" opacity="0.88"/>
    <circle cx="210" cy="205" r="42" fill="#ffffff" opacity="0.82"/>
    <circle cx="315" cy="190" r="46" fill="#ffffff" opacity="0.82"/>
    <circle cx="425" cy="210" r="40" fill="#ffffff" opacity="0.82"/>
    <rect x="175" y="240" width="285" height="44" rx="18" fill="{accent}" opacity="0.72"/>
    <text x="320" y="350" text-anchor="middle" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#1f2937">{title}</text>
    <text x="320" y="382" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" fill="#4b5563">{safe_subtitle}</text>
  </svg>'''
    return f"data:image/svg+xml,{quote(svg)}"


def task1_prompt(text: str) -> str:
    return f"""Task 1. You are going to read the text aloud. You have 1.5 minutes to read the text silently, then be ready to read it aloud. Remember that you will not have more than 1.5 minutes for reading aloud.

{text}"""


def make_task1_question(question_id: str, text: str) -> Question:
    return Question(
        id=question_id,
        task_type="task1",
        prompt_text=task1_prompt(text),
        reference_text=text,
        audio=QuestionAudio(intro="/audio/ege/task1/intro.mp3"),
        prep_seconds=90,
        record_seconds=90,
    )


def make_task2_question(
    question_id: str,
    *,
    variant: int,
    advertisement_title: str,
    advertisement_subtitle: str,
    context: str,
    prompts: list[str],
) -> Question:
    prompt_lines = "\n".join(f"{index}) {point}" for index, point in enumerate(prompts, start=1))
    return Question(
        id=question_id,
        task_type="task2",
        prompt_text=f"""Task 2. Study the advertisement.

{advertisement_title}
{advertisement_subtitle}

{context} In 1.5 minutes you are to ask four direct questions to find out about the following:

{prompt_lines}

You have 20 seconds to ask each question.""",
        task2_prompts=prompts,
        audio=QuestionAudio(
            intro=f"/audio/ege/task2/variant{variant:02d}/intro.mp3",
            question_cues=[
                f"/audio/ege/task2/variant{variant:02d}/q1.mp3",
                f"/audio/ege/task2/variant{variant:02d}/q2.mp3",
                f"/audio/ege/task2/variant{variant:02d}/q3.mp3",
                f"/audio/ege/task2/variant{variant:02d}/q4.mp3",
            ],
        ),
        prep_seconds=90,
        record_seconds=80,
    )


def task3_grading_prompt(topic: str, intro: str, questions: list[str]) -> str:
    return f"""Task 3. You are going to give an interview. You have to answer five questions. Give full answers to the questions: 2–3 sentences. Remember that you have 40 seconds to answer each question.

Interviewer intro:
{intro}

Questions:
{chr(10).join(f'{index + 1}) {question}' for index, question in enumerate(questions))}"""


def make_task3_question(question_id: str, *, variant: int, topic: str, questions: list[str]) -> Question:
    intro = f"Hello! It's Teenagers Round the World Channel. Our guest today is a teenager from Russia and we are going to discuss {topic}. Please answer five questions. So, let's get started."
    return Question(
        id=question_id,
        task_type="task3",
        prompt_text="""Task 3. You are going to give an interview. You have to answer five questions.

Give full answers to the questions: 2–3 sentences.

Remember that you have 40 seconds to answer each question.

The questions are played by the interviewer and are not shown on the screen, closer to the real exam format.""",
        grading_prompt_text=task3_grading_prompt(topic, intro, questions),
        interviewer_intro=intro,
        interview_questions=questions,
        audio=QuestionAudio(
            intro=f"/audio/ege/task3/variant{variant:02d}/intro.mp3",
            question_cues=[
                f"/audio/ege/task3/variant{variant:02d}/q1.mp3",
                f"/audio/ege/task3/variant{variant:02d}/q2.mp3",
                f"/audio/ege/task3/variant{variant:02d}/q3.mp3",
                f"/audio/ege/task3/variant{variant:02d}/q4.mp3",
                f"/audio/ege/task3/variant{variant:02d}/q5.mp3",
            ],
            end="/audio/ege/common/interview_end.mp3",
        ),
        prep_seconds=0,
        record_seconds=200,
    )


def make_task4_question(
    question_id: str,
    *,
    variant: int,
    project_title: str,
    photo1: str,
    photo2: str,
    advantages_phrase: str,
    disadvantages_phrase: str,
    opinion_phrase: str,
    colors: tuple[str, str, str, str],
) -> Question:
    prompt_text = f"""Task 4. Imagine that you and your friend are doing a school project “{project_title}”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

In 2.5 minutes be ready to:

• explain the choice of the illustrations for the project by briefly describing them and noting the differences;
• mention the advantages (1–2) of {advantages_phrase};
• mention the disadvantages (1–2) of {disadvantages_phrase};
• express your opinion on the subject of the project — {opinion_phrase}.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously."""
    grading_prompt = f"""Task 4. Imagine that you and your friend are doing a school project “{project_title}”. You have found two photos to illustrate it but for technical reasons you cannot send them now. Leave a voice message to your friend explaining your choice of the photos and sharing some ideas about the project.

Photo 1: {photo1}.
Photo 2: {photo2}.

In 2.5 minutes be ready to:
- explain the choice of the illustrations for the project by briefly describing them and noting the differences;
- mention the advantages (1–2) of {advantages_phrase};
- mention the disadvantages (1–2) of {disadvantages_phrase};
- express your opinion on the subject of the project — {opinion_phrase}.

You will speak for not more than 3 minutes: 12–15 sentences. You have to talk continuously."""
    bg1, accent1, bg2, accent2 = colors
    return Question(
        id=question_id,
        task_type="task4",
        prompt_text=prompt_text,
        grading_prompt_text=grading_prompt,
        image_urls=[
            make_svg_data_uri("Photo 1", photo1, bg1, accent1),
            make_svg_data_uri("Photo 2", photo2, bg2, accent2),
        ],
        image_captions=["Photo 1", "Photo 2"],
        audio=QuestionAudio(
            intro=f"/audio/ege/task4/variant{variant:02d}/intro.mp3",
            start_cue="/audio/ege/common/start_speaking.mp3",
        ),
        prep_seconds=150,
        record_seconds=180,
    )


TASK1_VARIANTS: list[tuple[str, str]] = [
    ("snowflakes", """Snowflakes are ice crystals which fall through the Earth's atmosphere as snow. People like to think that every snowflake has a unique shape. However, it is not true. While snowflakes may look different, they can still be classified into eight groups and about eighty different variants. Some scientists have done a lot of research into making a kind of catalogue of snowflakes.

The most typical patterns for a snowflake are needles, columns, plates and rimes. The shape and the pattern of a snowflake largely depend on the weather conditions. The study of snowflakes has identified that long, thin needle-like ice crystals form at around zero, while a lower temperature will lead to very flat crystals. Further changes in temperature as a snowflake falls determine more complicated shapes of snowflakes. The size of a snowflake also depends on the air temperature."""),
    ("urban_trees", """Urban trees are more important than many people think. In summer, streets with trees are usually cooler than streets without them. Leaves give shade and also release water into the air, which helps reduce heat. Trees can also improve air quality because they catch dust and absorb some harmful gases. In busy cities this is especially useful near roads and schools.

Another benefit of urban trees is psychological. Studies show that people often feel calmer and more focused when they can see green spaces from their windows. Even a small park can make a neighbourhood more pleasant. However, city trees need regular care. Their roots may be damaged by roads, and young trees need enough water. If cities want to become healthier places, planting and protecting trees should be part of long-term planning."""),
    ("ocean_currents", """Ocean currents are large movements of water that travel through the seas. Some currents move near the surface, while others flow deep below. They are caused by wind, differences in water temperature, the amount of salt in the water and the rotation of the Earth. Although currents may seem far away from everyday life, they influence the climate of many countries.

Warm currents can make coastal areas milder in winter, while cold currents may cool the air above them. Currents also carry nutrients, which are important for fish and other sea animals. That is why some fishing areas are especially rich. Today scientists study ocean currents very carefully because climate change can affect their speed and direction. Even small changes in these systems may have serious consequences for weather, sea life and people living near the coast."""),
    ("honeybees", """Honeybees are famous for producing honey, but their role in nature is much wider. When bees fly from flower to flower, they carry pollen. This process helps many plants produce fruit and seeds. Without bees and other pollinating insects, people would have fewer apples, berries, vegetables and nuts.

Bees live in organised colonies. Each bee has a role, and the colony works as one system. Worker bees collect food, care for young bees and protect the hive. Bees can also communicate with each other. When a worker bee finds a good source of food, it performs a special movement called a waggle dance. This dance tells other bees the direction and distance to the flowers. Unfortunately, bee populations are under pressure because of pesticides, diseases and loss of natural habitats. Protecting bees means protecting food production and biodiversity."""),
    ("public_libraries", """Public libraries have changed a lot over the last century. In the past, people mainly visited libraries to borrow books or read newspapers. Today libraries still offer books, but they also provide access to computers, online databases, language courses and cultural events. For many people, a library is one of the few quiet places where they can study or work for free.

Libraries are especially important for children and teenagers. They help young people discover reading and learn how to search for reliable information. Librarians can recommend books, explain how to use digital resources and organise educational activities. In small towns, a library may also become a community centre where people meet and share ideas. Even in the age of the Internet, public libraries remain valuable because they give equal access to knowledge."""),
    ("volcanic_ash", """When a volcano erupts, it can send clouds of ash high into the atmosphere. Volcanic ash is not soft like the ash left after a fire. It is made of tiny pieces of rock and glass. These particles can be dangerous for people, animals and machines. If ash gets into engines, it may cause serious damage. This is why flights are often cancelled after large eruptions.

At the same time, volcanic ash can have positive effects in the long term. When it falls on the ground and breaks down, it adds minerals to the soil. In some regions, land near volcanoes is very fertile, and farmers can grow good crops there. Scientists monitor active volcanoes to warn people about possible eruptions. Modern technology helps reduce risks, but living near a volcano still requires careful planning."""),
    ("electric_buses", """Electric buses are becoming more common in modern cities. Unlike traditional buses, they do not produce exhaust gases while they move through the streets. This can make city air cleaner, especially in areas with heavy traffic. Electric buses are also usually quieter, so they can reduce noise pollution near schools, hospitals and residential buildings.

However, electric transport needs careful planning. Cities must build charging stations and choose routes that match the battery capacity of the buses. Cold weather can also influence how long a battery lasts. Despite these difficulties, many transport experts believe that electric buses will play an important role in the future. They can help cities become cleaner and more comfortable, especially if the electricity comes from renewable sources."""),
    ("coral_reefs", """Coral reefs are sometimes called the rainforests of the sea because they support a huge variety of life. They are built by tiny animals called coral polyps. Over many years, these animals create large structures where fish, crabs and many other sea creatures can live. Reefs also protect coastlines by reducing the power of waves during storms.

Today coral reefs are in danger. Rising sea temperatures can cause coral bleaching, a process in which corals lose the tiny organisms that give them colour and food. Pollution and careless tourism can also damage reefs. Scientists and local communities are trying to protect these ecosystems by creating marine parks and reducing pollution. Saving coral reefs is important not only for nature, but also for people who depend on fishing and tourism."""),
    ("sleep_research", """Sleep is not just a period of rest. While people are asleep, the brain remains active and performs many important tasks. It organises memories, processes emotions and helps the body recover. Teenagers often need more sleep than adults because their brains and bodies are still developing.

Many students do not sleep enough during the school year. They may stay up late doing homework, using their phones or preparing for tests. Lack of sleep can make it harder to concentrate, remember information and control emotions. Researchers recommend having a regular sleep schedule and avoiding bright screens before bedtime. Good sleep habits can improve school performance and general health. Although sleep may seem like lost time, it is actually one of the best ways to prepare for a productive day."""),
    ("ancient_maps", """Ancient maps tell us a lot about how people understood the world in the past. Early mapmakers did not have satellites or modern instruments, so they used stories from travellers, observations of the stars and measurements made during journeys. Some maps were not completely accurate, but they were still very useful for trade, exploration and military planning.

Maps also reflected culture and imagination. Unknown lands were sometimes decorated with drawings of strange animals or dangerous seas. As navigation improved, maps became more detailed and reliable. The invention of printing helped spread them more widely. Today historians study old maps to learn about science, politics and communication between countries. A map is not only a practical tool; it is also a record of human curiosity."""),
    ("vertical_farms", """Vertical farms grow plants inside buildings, often on shelves placed one above another. Instead of soil, many of these farms use water with nutrients. Special lamps provide the light that plants need. This method allows people to grow vegetables in cities, close to the places where they will be sold and eaten.

One advantage of vertical farming is that it uses less land than traditional agriculture. It can also save water because the same water can be reused many times. Farmers can control temperature, light and humidity, so plants are protected from bad weather. However, vertical farms need electricity, and the equipment can be expensive. Researchers are working to make the technology cheaper and more energy-efficient. In the future, vertical farms may become an important part of urban food production."""),
    ("paper_recycling", """Paper recycling helps reduce the number of trees cut down for new paper products. When used paper is collected, it is cleaned, mixed with water and turned into a soft material called pulp. This pulp can then be used to make new paper, cardboard and packaging. Recycling also saves space in landfills and reduces waste.

However, paper cannot be recycled forever. Each time it goes through the process, the fibres become shorter and weaker. That is why recycled paper is often mixed with some new material. People can support recycling by separating paper from other rubbish and keeping it clean and dry. Schools and offices can also reduce paper use by printing less and using digital documents. Recycling is useful, but the best solution is to use resources more carefully from the beginning."""),
    ("desert_animals", """Desert animals live in some of the most difficult conditions on Earth. During the day, temperatures can be extremely high, while nights may be surprisingly cold. Water is rare, so animals have developed special ways to survive. Some get most of the water they need from food, while others can go for a long time without drinking.

Many desert animals are active at night. This helps them avoid the strongest heat of the day. Some hide underground, where the temperature is more stable. Light-coloured fur or skin can reflect sunlight, and large ears may help release heat. These adaptations show how living things can change over time to suit their environment. Deserts may look empty, but they are full of animals that are perfectly suited to life there."""),
    ("satellites", """Satellites are objects that move around planets or other bodies in space. Some are natural, like the Moon, while others are made by people. Artificial satellites are used for communication, weather forecasting, navigation and scientific research. They send signals and images back to Earth, helping people understand our planet and the universe.

Weather satellites can show the movement of clouds and storms, which helps meteorologists make forecasts. Navigation satellites allow phones and cars to find their position almost anywhere in the world. Scientists also use satellites to monitor forests, oceans and ice. However, the growing number of satellites creates a problem called space debris. Old parts and broken satellites can remain in orbit for years. Engineers are now looking for ways to make space activity safer and more sustainable."""),
    ("memory", """Human memory is not like a video recording. When people remember an event, the brain reconstructs it from different pieces of information. This means that memories can change over time. Emotions, new experiences and even other people's stories can influence what we think we remember.

There are different types of memory. Short-term memory helps us hold information for a brief period, such as a phone number we are about to write down. Long-term memory stores knowledge, skills and personal experiences. Sleep, attention and repetition all play important roles in remembering information. Students often learn better when they study regularly instead of trying to remember everything the night before a test. Understanding how memory works can help people learn more effectively."""),
    ("bridges", """Bridges are among the most important structures created by engineers. They allow people, cars and trains to cross rivers, valleys and busy roads. Some bridges are simple and short, while others are huge constructions that take years to build. The design of a bridge depends on the distance it must cover, the materials available and the weight it needs to carry.

Modern bridges often use steel and concrete, but older bridges were made of wood or stone. Engineers must consider wind, temperature changes and the movement of traffic. A bridge must be strong, but it also needs regular inspection and repair. Famous bridges often become symbols of their cities because they combine practical use with impressive design. They remind us that engineering can be both useful and beautiful."""),
    ("museums", """Museums help preserve objects that tell stories about history, science, art and culture. Some museums display paintings and sculptures, while others focus on technology, nature or everyday life in the past. By visiting museums, people can see real objects instead of only reading about them in books or online.

Modern museums are becoming more interactive. Many of them use screens, audio guides and virtual reality to help visitors understand exhibitions better. Some museums organise workshops where children can do experiments or create their own art. Museums also work with researchers to study and protect valuable collections. Although many things can now be viewed on the Internet, museums remain important because they give people a direct connection with human knowledge and creativity."""),
    ("wind_power", """Wind power is one of the oldest sources of energy used by people. In the past, windmills helped grind grain and pump water. Today modern wind turbines produce electricity. When the wind turns the blades of a turbine, a generator changes this movement into electrical energy.

Wind power has several advantages. It does not produce air pollution while generating electricity, and the wind itself is free. Wind farms can be built on land or at sea, where winds are often stronger. However, wind energy also has limitations. Turbines do not work when there is too little or too much wind. Some people dislike the way wind farms look, and birds can be affected if turbines are placed in the wrong areas. Careful planning helps reduce these problems."""),
    ("microplastics", """Microplastics are very small pieces of plastic, often smaller than a grain of rice. They come from larger plastic objects that break down over time, as well as from some clothes and cosmetics. Because they are so small, microplastics can easily spread through rivers, oceans, soil and even the air.

Scientists have found microplastics in fish, drinking water and remote natural areas. It is still not fully clear how they affect human health, but many researchers are concerned. Animals may mistake these particles for food, which can harm their bodies. Reducing plastic waste is one way to limit the problem. People can use reusable bags and bottles, choose products with less packaging and recycle properly. Microplastics show that even tiny pieces of waste can become a global environmental issue."""),
    ("robotics", """Robots are machines that can perform tasks automatically. Some robots work in factories, where they build cars or package products. Others help doctors during operations or explore places that are too dangerous for humans, such as deep oceans or damaged buildings. Robots can be controlled by people or programmed to make simple decisions.

The development of robotics depends on many areas of science and technology. Engineers design the body of a robot, while programmers create the software that controls it. Sensors allow robots to collect information about their surroundings. As robots become more advanced, people discuss how they should be used responsibly. Robots can make work safer and more efficient, but they may also change the job market. This is why education and planning are important in a robotic future."""),
]

TASK2_VARIANTS = [
    ("clinic", "THE BEST CLINIC IN TOWN!", "Professional care for the whole family!", "You are considering visiting the clinic and now you would like to get more information.", ["location", "public transport", "dentist", "family discounts"]),
    ("sports_centre", "ACTIVE LIFE SPORTS CENTRE", "Fitness, swimming and team games for everyone!", "You are considering visiting the sports centre and now you would like to get more information.", ["location", "opening hours", "swimming pool", "family discounts"]),
    ("bicycle_tour", "CITY BIKE TOUR", "See the city in a new way!", "You are considering taking part in the bicycle tour and now you would like to get more information.", ["starting point", "duration", "bike rental", "guide"]),
    ("art_museum", "MODERN ART MUSEUM", "Discover young artists and new ideas!", "You are considering visiting the art museum and now you would like to get more information.", ["opening hours", "ticket price", "guided tours", "photo permission"]),
    ("summer_camp", "GREEN VALLEY SUMMER CAMP", "Make friends and enjoy nature!", "You are considering going to the summer camp and now you would like to get more information.", ["dates", "accommodation", "activities", "transfer from the railway station"]),
    ("bookshop", "READ MORE BOOKSHOP", "Books, gifts and cosy reading corners!", "You are considering visiting the bookshop and now you would like to get more information.", ["location", "opening hours", "English books", "discount cards"]),
    ("dance_studio", "MOVE DANCE STUDIO", "Modern dance classes for teenagers!", "You are considering joining the dance studio and now you would like to get more information.", ["beginner groups", "class schedule", "price per month", "trial lesson"]),
    ("photo_course", "PHOTO START COURSE", "Learn to take better photos in four weeks!", "You are considering taking the photo course and now you would like to get more information.", ["course duration", "equipment needed", "teacher experience", "final project"]),
    ("pet_hotel", "HAPPY PAWS PET HOTEL", "Safe care for your pets while you travel!", "You are considering using the pet hotel and now you would like to get more information.", ["location", "daily price", "food included", "veterinary care"]),
    ("science_club", "YOUNG SCIENTISTS CLUB", "Experiments, projects and discoveries!", "You are considering joining the science club and now you would like to get more information.", ["age limits", "meeting days", "laboratory equipment", "competitions"]),
    ("online_library", "DIGITAL READING LIBRARY", "Thousands of books on your device!", "You are considering using the online library and now you would like to get more information.", ["subscription price", "number of books", "offline reading", "student discounts"]),
    ("volunteer_project", "HELPING HANDS PROJECT", "Join local volunteering events!", "You are considering joining the volunteer project and now you would like to get more information.", ["activities", "minimum age", "weekend events", "certificate"]),
    ("cooking_class", "TEEN COOKING CLASS", "Cook simple and healthy meals!", "You are considering joining the cooking class and now you would like to get more information.", ["location", "class size", "ingredients included", "vegetarian dishes"]),
    ("robotics_workshop", "ROBOTICS WEEKEND", "Build and program your first robot!", "You are considering taking part in the robotics workshop and now you would like to get more information.", ["dates", "required skills", "materials", "team project"]),
    ("music_school", "NEW SOUND MUSIC SCHOOL", "Learn guitar, piano and singing!", "You are considering studying at the music school and now you would like to get more information.", ["instruments", "individual lessons", "concerts", "monthly fee"]),
    ("skating_rink", "ICE WORLD SKATING RINK", "Enjoy skating with friends!", "You are considering visiting the skating rink and now you would like to get more information.", ["opening hours", "ticket price", "skate rental", "coach"]),
    ("language_trip", "ENGLISH WEEKEND TRIP", "Practise English outside the classroom!", "You are considering going on the language trip and now you would like to get more information.", ["destination", "travel dates", "accommodation", "speaking practice"]),
    ("eco_shop", "GREEN CHOICE ECO SHOP", "Reusable products for everyday life!", "You are considering buying something from the eco shop and now you would like to get more information.", ["location", "online orders", "product range", "discounts for students"]),
    ("career_fair", "FUTURE JOBS FAIR", "Meet universities and employers!", "You are considering visiting the career fair and now you would like to get more information.", ["date", "participants", "entry fee", "career tests"]),
    ("swimming_course", "SUMMER SWIMMING COURSE", "Improve your swimming skills!", "You are considering joining the swimming course and now you would like to get more information.", ["pool location", "lesson times", "group size", "medical certificate"]),
]

TASK3_VARIANTS = [
    ("accommodation", "teenagers' attitude to their accommodation", ["In what region do you live? Do you live in a big city, a town or in a village?", "Do you live in a flat or in a house? What is it like?", "What would you like to change about your flat or house? Why?", "What do you like and dislike about your neighbourhood?", "What kind of housing would you like to have in the future?"]),
    ("hobbies", "hobbies", ["What hobbies are popular among teenagers in your region?", "What hobby do you have? How much time do you spend on it?", "Do you prefer hobbies that you can do alone or with other people? Why?", "Can hobbies help teenagers with their future career? Why or why not?", "What new hobby would you like to try in the future?"]),
    ("school_life", "school life", ["What subjects do you study at school this year?", "Which school subject do you find the most useful? Why?", "How much homework do you usually get? Is it too much in your opinion?", "What school event do you remember best? Why was it special?", "What would you change in your school if you could?"]),
    ("healthy_lifestyle", "a healthy lifestyle", ["What do teenagers in your region usually do to stay healthy?", "Do you do any sport or physical exercise? How often?", "What food do you think is healthy for teenagers? Why?", "Is it difficult for students to sleep enough during the school year? Why?", "What healthy habit would you like to develop in the future?"]),
    ("future_career", "future careers", ["What job would you like to have in the future?", "Who or what has influenced your career choice?", "What skills are important for your future profession? Why?", "Would you prefer to work alone or in a team? Why?", "Do you think teenagers should start thinking about their career early? Why or why not?"]),
    ("free_time", "free time", ["How much free time do you usually have on weekdays?", "What do you prefer to do when you have a free evening?", "Do you like spending your free time at home or outside? Why?", "How do smartphones influence teenagers' free time?", "What would you do if you had one completely free day?"]),
    ("travelling", "travelling", ["Do you like travelling? Why or why not?", "What places in Russia would you recommend tourists to visit?", "Do you prefer travelling with your family or with friends? Why?", "What problems can people have while travelling?", "Where would you like to travel in the future?"]),
    ("reading", "reading habits", ["Do teenagers in your region read much? Why do you think so?", "What kind of books do you enjoy reading?", "Do you prefer paper books or e-books? Why?", "Can films replace books? Why or why not?", "What book would you recommend to a friend?"]),
    ("internet", "the Internet", ["How often do you use the Internet?", "What do you usually use the Internet for?", "Can the Internet help students learn better? How?", "What dangers can teenagers face online?", "Would you like to spend less time online? Why or why not?"]),
    ("food", "food and eating habits", ["What food is popular among teenagers in your region?", "Do you usually eat at home or at school?", "Can teenagers cook healthy meals themselves? Why?", "Why do some people prefer fast food?", "What dish would you like to learn to cook?"]),
    ("sports", "sports", ["What sports are popular in your school?", "Do you prefer team sports or individual sports? Why?", "How often should teenagers do physical exercise?", "Can watching sport be as interesting as doing sport? Why?", "What sport would you like to try one day?"]),
    ("family", "family life", ["How much time do you spend with your family?", "What activities do you enjoy doing with your relatives?", "Do teenagers usually ask their parents for advice? Why?", "What household chores do you do at home?", "What family tradition would you like to keep in the future?"]),
    ("friends", "friendship", ["How do you usually spend time with your friends?", "What qualities are important in a good friend?", "Can online friends be as close as real-life friends? Why?", "Do friends influence teenagers' choices? How?", "How can people keep friendship for many years?"]),
    ("environment", "environmental problems", ["What environmental problems are common in your region?", "Do you and your classmates do anything to help nature?", "Is recycling popular among teenagers? Why or why not?", "What can schools do to become more eco-friendly?", "What environmental habit would you like to develop?"]),
    ("technology", "modern technology", ["What gadgets do you use every day?", "How does technology help you study?", "Can teenagers spend too much time using gadgets? Why?", "What technology would you find difficult to live without?", "What new invention would you like to see in the future?"]),
    ("shopping", "shopping", ["Do you like shopping? Why or why not?", "What do teenagers usually buy most often?", "Do you prefer shopping online or in real shops? Why?", "How can advertising influence teenagers?", "What would you never buy online?"]),
    ("movies", "films and cinema", ["How often do you watch films?", "What kind of films do you enjoy most?", "Do you prefer watching films at home or at the cinema? Why?", "Can films teach people something useful?", "What film would you recommend to a foreign friend?"]),
    ("city_life", "city life", ["What do you like about the place where you live?", "What problems do people have in big cities?", "Would you prefer to live in a city or in the countryside? Why?", "What public places are popular with teenagers in your town?", "How could your town or city be improved?"]),
    ("holidays", "holidays and celebrations", ["What holidays are most popular in your family?", "How do you usually celebrate your birthday?", "Do you prefer quiet family celebrations or big parties? Why?", "Can holidays help people learn about culture?", "What celebration would you like to attend in another country?"]),
    ("learning_english", "learning English", ["How long have you been learning English?", "What is the most difficult thing about learning English for you?", "Do you prefer learning English with a teacher or by yourself? Why?", "How can films or songs help people learn a language?", "How do you plan to use English in the future?"]),
]

TASK4_VARIANTS = [
    ("weekend", "Ideal weekend", "a family is having a picnic in a park", "two teenagers are watching a film at home", "the two ways to spend the weekend", "the two ways to spend the weekend", "say which way of spending the weekend you prefer and why", ("#dcfce7", "#22c55e", "#dbeafe", "#3b82f6")),
    ("keeping_fit", "Keeping fit", "a young man is jogging in a park", "a young woman is exercising in a gym", "the two ways of keeping fit", "the two ways of keeping fit", "say which way of keeping fit you prefer and why", ("#fef3c7", "#f59e0b", "#e0e7ff", "#6366f1")),
    ("learning_languages", "Learning languages", "students are learning a foreign language in a classroom", "a teenager is having an online language lesson at home", "the two ways of learning languages", "the two ways of learning languages", "say which way of learning languages you prefer and why", ("#fce7f3", "#ec4899", "#ccfbf1", "#14b8a6")),
    ("future_career", "Choosing a future career", "a doctor is talking to a patient in a clinic", "a software developer is working at a computer in an office", "the two jobs shown in the photos", "the two jobs shown in the photos", "say which job you would prefer and why", ("#fee2e2", "#ef4444", "#dbeafe", "#2563eb")),
    ("eco_habits", "Eco-friendly habits", "a teenager is using a reusable water bottle", "a family is sorting rubbish for recycling", "the two eco-friendly habits shown in the photos", "the two eco-friendly habits shown in the photos", "say which habit is more important and why", ("#dcfce7", "#16a34a", "#f0fdf4", "#22c55e")),
    ("school_projects", "School projects", "students are making a poster together", "a teenager is preparing slides on a laptop", "the two ways of working on a school project", "the two ways of working on a school project", "say which way of preparing a project you prefer and why", ("#e0f2fe", "#0284c7", "#fae8ff", "#c026d3")),
    ("healthy_food", "Healthy food", "teenagers are eating a salad at school", "a family is cooking dinner at home", "the two ways of eating healthily", "the two ways of eating healthily", "say which way of eating healthily you prefer and why", ("#dcfce7", "#16a34a", "#ffedd5", "#f97316")),
    ("public_transport", "Public transport", "people are travelling by bus", "a teenager is riding a bicycle", "the two ways of getting around the city", "the two ways of getting around the city", "say which way of travelling around the city you prefer and why", ("#dbeafe", "#2563eb", "#dcfce7", "#16a34a")),
    ("volunteering", "Volunteering", "teenagers are cleaning a park", "a student is helping an elderly person with shopping", "the two types of volunteering", "the two types of volunteering", "say which type of volunteering you would choose and why", ("#f0fdf4", "#22c55e", "#fef3c7", "#d97706")),
    ("family_time", "Family time", "a family is playing a board game", "a family is walking outdoors", "the two ways of spending time with family", "the two ways of spending time with family", "say which way of spending time with family you prefer and why", ("#ede9fe", "#7c3aed", "#dcfce7", "#16a34a")),
    ("online_offline_shopping", "Shopping habits", "a teenager is shopping online", "friends are choosing clothes in a shop", "the two ways of shopping", "the two ways of shopping", "say which way of shopping you prefer and why", ("#dbeafe", "#2563eb", "#fce7f3", "#db2777")),
    ("reading_formats", "Reading today", "a student is reading a paper book", "a teenager is reading on an e-reader", "the two ways of reading", "the two ways of reading", "say which way of reading you prefer and why", ("#fef3c7", "#d97706", "#e0e7ff", "#4f46e5")),
    ("learning_places", "Places to study", "students are studying in a library", "a teenager is studying at home", "the two places to study", "the two places to study", "say which place to study you prefer and why", ("#f8fafc", "#64748b", "#dbeafe", "#2563eb")),
    ("free_time", "Free time", "teenagers are playing football outside", "a teenager is playing a computer game", "the two ways of spending free time", "the two ways of spending free time", "say which way of spending free time you prefer and why", ("#dcfce7", "#16a34a", "#e0e7ff", "#4f46e5")),
    ("travelling", "Travelling", "tourists are visiting a city museum", "a family is hiking in the mountains", "the two ways of travelling", "the two ways of travelling", "say which way of travelling you prefer and why", ("#fef3c7", "#d97706", "#dcfce7", "#16a34a")),
    ("communication", "Communication", "friends are talking in a cafe", "teenagers are chatting online", "the two ways of communication", "the two ways of communication", "say which way of communication you prefer and why", ("#fce7f3", "#db2777", "#dbeafe", "#2563eb")),
    ("workplaces", "Workplaces", "people are working in an office", "a person is working from home", "the two workplaces", "the two workplaces", "say which workplace you would prefer and why", ("#e5e7eb", "#4b5563", "#dbeafe", "#2563eb")),
    ("school_events", "School events", "students are performing on a stage", "students are taking part in a sports day", "the two types of school events", "the two types of school events", "say which school event you would prefer and why", ("#fae8ff", "#c026d3", "#dcfce7", "#16a34a")),
    ("technology_in_class", "Technology in class", "students are using tablets in a classroom", "a teacher is writing on a traditional board", "the two ways of using materials in class", "the two ways of using materials in class", "say which way of learning in class you prefer and why", ("#dbeafe", "#2563eb", "#f8fafc", "#64748b")),
    ("pets", "Pets in people's lives", "a teenager is walking a dog", "a child is feeding a cat at home", "the two ways of taking care of pets", "the two ways of taking care of pets", "say which pet care activity you prefer and why", ("#dcfce7", "#16a34a", "#ffedd5", "#f97316")),
]

TASK1_QUESTIONS = [
    make_task1_question(
        "demo_task1_snowflakes_001" if index == 1 else f"curated_task1_{slug}_{index:03d}",
        text,
    )
    for index, (slug, text) in enumerate(TASK1_VARIANTS, start=1)
]

TASK2_QUESTIONS = [
    make_task2_question(
        "demo_task2_clinic_001" if index == 1 else f"curated_task2_{slug}_{index:03d}",
        variant=index,
        advertisement_title=title,
        advertisement_subtitle=subtitle,
        context=context,
        prompts=prompts,
    )
    for index, (slug, title, subtitle, context, prompts) in enumerate(TASK2_VARIANTS, start=1)
]

TASK3_QUESTIONS = [
    make_task3_question(
        "demo_task3_accommodation_001" if index == 1 else f"curated_task3_{slug}_{index:03d}",
        variant=index,
        topic=topic,
        questions=questions,
    )
    for index, (slug, topic, questions) in enumerate(TASK3_VARIANTS, start=1)
]

TASK4_QUESTIONS = [
    make_task4_question(
        "demo_task4_weekend_001" if index == 1 else f"curated_task4_{slug}_{index:03d}",
        variant=index,
        project_title=project_title,
        photo1=photo1,
        photo2=photo2,
        advantages_phrase=advantages_phrase,
        disadvantages_phrase=disadvantages_phrase,
        opinion_phrase=opinion_phrase,
        colors=colors,
    )
    for index, (slug, project_title, photo1, photo2, advantages_phrase, disadvantages_phrase, opinion_phrase, colors) in enumerate(TASK4_VARIANTS, start=1)
]

ALL_CURATED_QUESTIONS = [
    *TASK1_QUESTIONS,
    *TASK2_QUESTIONS,
    *TASK3_QUESTIONS,
    *TASK4_QUESTIONS,
]

DEMO_QUESTIONS_BY_TASK_TYPE: dict[str, Question] = {
    "task1": TASK1_QUESTIONS[0],
    "task2": TASK2_QUESTIONS[0],
    "task3": TASK3_QUESTIONS[0],
    "task4": TASK4_QUESTIONS[0],
}

ALL_CURATED_QUESTIONS_BY_ID = {
    question.id: question
    for question in ALL_CURATED_QUESTIONS
}


def get_demo_question(task_type: str) -> Question | None:
    return DEMO_QUESTIONS_BY_TASK_TYPE.get(task_type)


def get_question_by_id(question_id: str) -> Question | None:
    return ALL_CURATED_QUESTIONS_BY_ID.get(question_id)


def get_question_seed_items() -> list[tuple[Question, bool, int]]:
    seed_items: list[tuple[Question, bool, int]] = []

    for questions in [TASK1_QUESTIONS, TASK2_QUESTIONS, TASK3_QUESTIONS, TASK4_QUESTIONS]:
        for position, question in enumerate(questions, start=1):
            seed_items.append((question, position == 1, position))

    return seed_items
