# Руководство: Наглядная сейсмология

**Цель** репозитория &ndash; структурирование опыта работы с *сейсмологическими данными* и *визуализацией информации* в формате интерактивных тетрадей *Jupyter Notebook*. В руководстве представлена попытка[^1] резюмирования актуальной информации о доступном сейсмологу наборе программных инструментов с открытым исходным кодом. Использование языка программирования *Python* в качестве связующей основы позволяет объединить их функционал для эффективного решения ряда сейсмологических задач и эффектной визуализации результатов.

[^1]: Попытка резюмирования актуальной информации предпринята впервые, хотя идеи о кратком конспектировании накопившихся знаний в цифровом виде возникали у автора давно: ещё до начала аспирантуры (2016) и задолго до защиты диссертации (2021). Ключевым толчком стала недавняя необходимость в проведении занятий по блоку сейсмологии со студентами. Конечная цель &ndash; создать в репозитории качественное и обширное руководство, а также дополнить его практическими заданиями для студентов (practice), примерами решения конкретных небольших задачек (cookbook) и собственными лекциями об основах и спецефичных разделах сейсмологии.


### :bookmark_tabs: Содержание
Файлы интерактивных тетрадей с расширением `.ipynb` в данной директории пронумерованы и названы в соответствии с их содержанием:

- ~~[**Знакомство с ObsPy**]~~
    - Лекция в доработке, следите за обновлениями
- [**Постер о землетрясении**](Earthquake%20Poster%20LASTNAME.ipybn)
    - Практическое задание

### :raised_hand: Прежде чем начать

Для полноценных занятий имеет смысл обзавестись локальной копией руководства. Для этого достаточно скачать данный репозиторий в виде архива с ***GitHub***:
:octocat: https://github.com/abramsci/seismology/archive/refs/heads/ru.zip
И извлечь содержимое папки в желаемую директорию.

>   ***Система контроля версий [Git](https://git-scm.com/)*** :pray:
>   <details>
>   <summary><i>Клонирование репозитория через командную строку</i></summary>
>   Более элегантный способ скачать руководство:
>
>   0. Установить git
>
>   1. Запустить терминал:
>       - В **Windows** достаточно нажать сочетание клавиш *Win+R*, в появившемся окне/строке ввести `powershell` и нажать *Enter*
>       - В **MacOS** схожим образом можно нажать *Cmd+Пробел*, в появившейся строке начать вводить `Terminal` и выбрать приложение
>       - В **Linux** не задают вопроса как запустить терминал :neckbeard:
>
>   2. Перейти в существующую рабочую директорию куда планируется склонировать репозиторий (например, :file_folder:<ins>*D:\study*</ins> или :file_folder:<ins>*~/study*</ins>)
>       ```sh
>       # Переход по абсолютному пути Windows
>       cd D:\study
>       # В случае MacOS / Linux
>       cd ~/study
>       ```
>   3. Cклонировать репозиторий :wink:
>       ```sh
>       git clone https://github.com/abramsci/seismology.git
>       ```
>   При клонировании будет создана папка с названием репозитория (в нашем случае :file_folder:<ins>*seismology*</ins>) со всем его содержимым. Руководство, разделенное по частям на интерактивные тетради, находится в папке :file_folder:<ins>*tutorial*</ins>.
>   </details>

***Контрольный список готовности к работе:***

0. :file_folder: Имеется локальная копия руководства (см. выше)
1. [:computer:](#conda-install) На компьютере установлен дистрибутив *conda*
2. [:construction:](#env-create) Для работы создано окружение (*environment*)
3. [:heavy_plus_sign:](#kernel-add) Окружение добавлено в *Jupyter Notebook*

Далее пошагово разбирается процесс установки и настройки всего необходимого для работы с тетрадями &ndash; иконки в списке выше можно кликнуть, чтобы перейти к интересующему шагу.


#### :computer: Установка менеджера пакетов *conda* {#conda-install}

***Если conda установлена, двигаемся дальше*** [:fast_forward:](#env-create)

Для знакомства с миром наглядной сейсмологии помимо ~~необходимости~~ желания нам нужно программное обеспечение. Необходимый минимум начинается с браузера и *менеджера пакетов*[^2] [*conda*](https://docs.conda.io/en/latest/index.html). Браузер почти наверняка предустановлен[^3] в операционной системе по умолчанию и скорее всего уже заменен на более популярный (*Chrome*, *Firefox*, etc.).  Наличие же дистрибутива *conda* на компьютере вовсе не гарантировано, но намекает на заинтересованность владельца в изучении языков программирования *Python/R*, работе в области *Data Science* или освоении набравших популярность инструментов *Machine Learning*.

[^2]: Строго говоря, *conda* &ndash; это не только менеджер пакетов, но и система управления рабочими окружениями. Пояснения в тексте [:rewind:](#env-create)
[^3]: Предустановлен ли браузер &ndash; вопрос хороший. Почти наверняка программа выполняющая функцию просмотра веб-страниц через интернет-протоколы в операционной системе имеется. Исключением может быть разве что супер-минималистичная версия *ArchLinux*, но в таком случае владелец компьютера вряд ли нуждается в пояснениях, что такое браузер и есть ли он у него :smile:. *Jupyter Notebook* при запуске без соответствующей опции использует программу, выставленную в системе браузером по умолчанию.

Существуют два основных дистрибутива *conda* ([советы по выбору](https://docs.conda.io/projects/conda/en/latest/user-guide/install/download.html#anaconda-or-miniconda)):  
- [*Anaconda*](https://www.anaconda.com/products/distribution) &ndash; ~~тяжеловесный~~ привычный студентам / новичкам вариант:
    - в комплекте со старта идет множество научных пакетов *Python*
    - имеет графический интерфейс *Anaconda Navigator*
- [*miniconda*](https://docs.conda.io/en/latest/miniconda.html) &ndash; минималистичный вариант для продвинутых инженеров:
    - экономит место в директории установки (со старта занимает ~500 Мб)
    - приучает к использованию командной строки (что полезно :neckbeard:)

Инсталятор для любой из поддерживаемых платформ с можно скачать с сайта, установка обычно не вызывает сложностей. Главным достоинством конды является возможность работы на уровне прав пользователя. На практике это означает, что для установки пакетов и создания рабочего окружения на компьютере не требуются права администратора. Это весьма удобно, особенно для занятий на университетских / институтских компьютерах в общем пользовании. Такой подход добавляет устойчивости и безопасности, ведь у неопытного пользователя меньше шансов "поломать" что-либо на уровне системы.

Для работы с интерактивными тетрадями необходим [*Jupyter*](https://jupyter.org/) *Notebook* или же *Jupyter Lab*. Нужно отметить, что руководство создается в первую очередь для *Jupyter Notebook*, как наиболее стандартного "студенческого" варианта знакомства с *Python*.

>   :heavy_check_mark: *Jupyter Notebook входит в дистрибутив **Anaconda***
>   <details>
>   <summary><i>В случае использования <b>miniconda</b></i></summary>
>   <i>Jupyter Notebook</i> &ndash; инструмент популярный, но немного тяжеловесный, поэтому в базовом окружении <b>miniconda</b> его нет. Однако, для работы с тетрадями в рамках данного руководства мы все равно будем создавать новое рабочее окружение и в случае использования miniconda просто добавим в него ещё и <i>Jupyter Notebook</i>. Это неплохое решение для ситуации, когда Jupyter Notebook постоянно не используется, а для написания и запуска python-скриптов достаточно простой связки текстового редактора и терминала. Подробнее о том что такое рабочее окружение и зачем оно нужно в следующей секции.
>   </details>

<ins>Альтернативно</ins>, можно использовать предпочитаемую *IDE*[^4], поддерживающую работу с тетрадями в формате `.ipybn`: например, [*VS Code*](https://code.visualstudio.com/) или [*PyCharm*](https://www.jetbrains.com/pycharm/). Тонкости запуска и настройки тетрадей в этих программах руководство не освещает, однако следующая секция о создании рабочего окружения все так же актуальна.

[^4]: IDE, *Integrated Development Environment* &ndash; комплекс программных средств, чаще всего включающий редактор кода, интерпертаторы/компиляторы, дебаггеры, профайлеры и прочие вкусности, пользы от которых для новичка в программировании не так много. Интегрированными средами разработки пользоваться удобно, однако они скрывают от глаз много важных взаимодействий. Профессионалы, которые и так представляют что происходит "под капотом" не в счет, а вот новичкам полезнее учится сначала работать в простейшей связке: текстовый редактор + терминал с установленным интерпретатором (например когда изучается *Python*) или компилятором (в случае *C / Fortran*).


#### :construction: Создание рабочего окружения {#env-create}

***Если есть опыт создания conda environment*** [:fast_forward:](#env-allinone)

***Conda*** &ndash; это не только весьма универсальный менеджер пакетов, но также и система управления *окружениями* ***conda environments***. Cоздание нового рабочего окружения позволит нам изолировать специфичные для сейсмологии пакеты *Python* и вспомогательные программы внутри отдельной папки в файловой системы. Таким образом мы оставляем базовое окружение *conda* нетронутым (и весьма минималистичным в случае *miniconda*).

>   :heavy_exclamation_mark: ***Используемые определения***
>   - **Окружение** &ndash; именно то, что понимается под *conda environment*, совокупность пакетов и интерпретатора *Python*, а также вспомогательных скомпилированных библиотек и программ (написанных например на языке *C*)
>   - **Рабочее окружение** &ndash; *функционирующий* вариант окружения с инструментами, необходимыми для работы с конкретной интерактивной тетрадью, практическим заданием или всем руководством
>
>   <details>
>   <summary><i>Подробнее о выборе терминологии</i></summary>
>   Важно было четко определить ключевые понятия приведенные выше, на которые опирается данное руководство и репозиторий в целом. Человек, хорошо знакомый с программированием и разработкой программного обеспечения может оспорить выбор терминов и предложить что-нибудь вроде словосочетаний "виртуальное окружение" или "среда выполнения". Пространная дискуссия о правильном переводе таких концептов как <i>virtual environment</i> и <i>runtime system</i> и о том, в какую из двух концепций укладывается конкретная реализация (<i>conda environment</i> &ndash; случай, когда пакеты загружаются в бинарном виде) &ndash; такая дискуссия собъет с толку неподготовленного человека. Руководство все же в первую очередь рассчитано на геофизиков (студентов и коллег), а не на матерых кодеров. Более того, и составляется руководство самоучкой: с пятнадцатилетним опытом программирования, но без реального опыта работы в "ай-ти" (когда платят з.п.).
>   </details>

Между окружениями можно свободно переключаться, что позволяет иметь различные комбинации инструментов для различных проектов / задач. Минус наличия большого количества окружений &ndash; необходимость хранения множества относительно тяжелых папок с их содержимым в файловой системе. Чтобы быть полностью независимым от других, окружению требуется наличие в собственной директории всего необходимого, в том числе и повторяющихся между окружениями версий пакетов и самого интерпретатора *Python*. Впрочем для работы с данным руководством будет достаточно одного рабочего окружения, в худшем случае пары-тройки :wink:.

Для работы с тетрадями в руководстве, а также для выполнения практического задания, нам потребуется несколько специализированных инструментов. Первый и основной среди них [ObsPy](https://docs.obspy.org/) &ndash; фреймворк языка программирования *Python* для работы с сейсмическими данными, заточенный под сейсмологические задачи. Для его работы требуется широко-используемый в *Data Science* "джентельменский набор" пакетов *Python*: *NumPy*, *SciPy*, *matplotlib*, *pandas*. Данные пакеты, в свою очередь, также имеют зависимости от нескольких более низкоуровневых модулей (*liblapack, mkl, openssl, etc.*), которых нет в стандартной библиотеке *Python*. Тут на сцену и выходит основной функционал **менеджера пакетов**, которым в нашем случае является все та же ***conda***!

>   :memo: *Почему в качестве менеджера пакетов не **pip**[^5]?*
>   <details>
>   <summary><i>Разница между <b>pip</b> и <b>conda</b></i></summary>
>   <b>pip (package installer for Python)</b> &ndash; это пакетный менеджер, заточенный под конкретный язык программирования. Приимуществом же <i>conda</i> является возможность легкой установки множества других, не относящихся к экосистеме <i>Python</i>, пакетов и программ: например <i>Generic Mapping Tools (GMT)</i>. Данный набор написанных на <i>C</i> консольных программ для создания высококачественой графики (в основном карт) является вторым из используемых в руководстве инструментов. Помимо этого, <i>conda</i> сомвещает в себе функционал менеджера пакетов и системы упревления рабочими окружениями. В случае использования <i>pip</i> роль менеджера окружений как правило выполняет отдельный инструмент: <i>venv, virtualenv, pyenv, etc</i>. И наконец, существенная разница ещё и в том, что <i>pip</i> скачивает исходный код и затем собирает / компилирует бинарные файлы для пакета если это необходимо &ndash; <i>conda</i> же сразу устанавливает бинарники, соответствующие целевой платформе, таким образом упрощая жизнь пользователю, если у него например не установлен какой-нибудь специфичный компилятор (например <i>gfortran</i> на <i>Windows</i>).
>   </details>

[^5]: См. [запись в блоге~anaconda-blog~](https://www.anaconda.com/blog/understanding-conda-and-pip)

Менеджер пакетов возмет на себя почти всю работу по выбору неконфликтующих версий, скачиванию необходимых нам пакетов, скачиванию всех их зависимостей и наконец самой установке. Руководство разделено на несколько частей и каждая тетрадь требует специфичный набор установленных пакетов, однако многие ключевые зависимости в разных пакетах одни и те же (например NumPy).

Если планируется полное прохождение руководства, то проще сразу создать рабочее окружение со всем необходимым и назвать его, например, [==seismology==](#env-allinone). Однако не исключено, что установка масштабного окружения в котором "всё включено" может споткнуться о какие-нибудь конфликты в версиях (см. пояснения ниже, в блоке об инструментах с открытым кодом). В таком случае проще создать несколько независимых но рабочих окружений, по одному для каждой части руководства или для нескольких смежных тетрадей. Помимо этого иногда интересует работа только с какой-либо конкретной тетрадью. Инструкции по созданию специфичных рабочих окружений приведены списком в [отдельной секции](#env-specifics).

>   :warning: *Используются инструменты с открытым исходным кодом!*
>   <details>
>   <summary><i>Помимо очевидных плюсов, есть и тонкости</i></summary>
>   Нет гарантий, что пакет / инструмент, приведенный в данном руководстве будет работать в будущем. Есть вероятность наткнуться на баги или несовместимую комбинацию пакетов, функционал которых опирается на различные версии общей зависимости. Подобным проблемам больше подвержены нишевые, подзаброшенные авторами, а также недавно стартовавшие и пока сырые проекты. Широко используемые комбинации с большой базой пользователей обычно работают без проблем. При подготовке данного руководства автор старается протестировать предложенные комбинации на максимально доступном спектре платформ / операционных систем, однако это весьма времязатратный процесс. Что важнее, поспевать за изменениями всех используемых инструментов с таким подходом крайне сложно, поэтому руководство потребуется время от времени актуализировать.
>   </details>

Важно помнить, что при наличии более-менее современного компьютера и интернет соединения создание и удаление рабочих окружений не занимает много времени. Поэтому если что-то пошло не так, достаточно удалить неудачное и попробовать создать новое. Однако, каждое окружение кроме базового создает собственную папку[^6] со всем своим содержимым внутри директории куда установлена конда. По-умолчанию все это находится в домашней папке пользователя, которая при создании пары-тройки окружений может раздуться до размеров нескольких гигабайт.

[^6]: Conda environment &ndash; папка с названием окружения внутри директории :file_folder:<ins>*envs*</ins>, расположенной по умолчанию там, где установлен дистрибутив *conda*. В случае рекомендуемой установки на уровне прав пользователя, дистрибутив располагается в его домашней папке и называется по имени дистрибутив и основной версии Python в базовом окружении (например :file_folder:<ins>*~/miniconda3*</ins> на MacOS/Linux или :file_folder:<ins>*C:\Users\IlonMusk\miniconda3*</ins>

После установки *conda* на компьютере впервые доступным будет только одно единственное базовое окружение ==base==. Создать новое окружение можно несколькими способами:  
- Через графический интерфейс *Anaconda Navigator* идущей в комплекте дистрибутива *Anaconda*
- Используя файл `environment.yml`, если таковой имеется
- Перечислив необходимые инструменты в одной командной строке
- Собрав окружение в несколько раздельных команд *conda*

Далее пошагово разбираются действия, необходимые для создания окружения с использованием командной строки. Все что от нас требуется в таком случае: подключение к интернету и запущенный терминал[^7], универсальный для обоих дистрибутивов *conda*. Создание нового окружения с использованием графического интерфейса в руководстве не рассматривается по причине тривиальности данного процесса.

[^7]: Строго говоря, *терминал*, *консоль*, *командная оболочка/интерпретатор* и *командная строка* &ndash; термины, имеющие конкретные значения, которые однако часто смешивают в разговоре и путают даже профессионалы. Далее приводится очень краткие определения, желающие преисполниться в познании и правильно использовать терминологию могут обратится к достаточно подробной [записи в блоге~geeksforgeeks~](https://www.geeksforgeeks.org/difference-between-terminal-console-shell-and-command-line/). *Терминал~terminal~* &ndash; система ввода и вывода текстовой информации (да, да, никаких картинок, хотя умельцы и делают ASCII графику). *Консоль~console~* &ndash; физическая манифестация терминала, например, клавиатура для ввода команд от пользователя к компьютеру и монитор для вывода информации обратно к пользователю (включая разумеется историю набранных команд). *Командная оболочка~shell~ или интерпретатор* &ndash; прослойка между пользователем и ядром операционной системы, которая обрабатывает команды и запускает программы передавая им опции и параметры, указанные в командной строке. *Командная строка~comand-line/prompt~* &ndash; активная строка внизу терминала, куда вводятся команды, над ней обычно располагается история работы: предыдущие введенные команды и результаты их *вывода~output~*.


##### :key: Запуск терминала, основные команды *conda*

В зависимости от операционной системы[^8]:

[^8]: В Linux и MacOS терминал, как правило, после установки конды понимает, что теперь у пользователя есть доступ к рабочим окружениям. В Windows также есть варианты настроить стандартный PowerShell на работу с кондой. Нам же будет проще запустить *Anaconda Prompt*, установленный по-умолчанию как в представительном *Anaconda*, так и легковесном *miniconda*. Проще будет вынести советы по работу в командной строке, настройке и использованию терминала на различных операционных системах в отдельную часть, так как тема эта весьма и весьма обширная. Но в данном руководстве, по крайней мере в текущей его итерации, это не слишком целесообразно.

**Windows:** *Пуск -> Anaconda3 -> Anaconda Prompt*
**Mac/Linux:** *обычно достаточно перезапустить стандартный терминал*

После запуска терминала обычно сверху вниз по строчкам выводится приветственная информация командной оболочки. Внизу располагается командная строка, готовая к работе. В достаточно стандартном виде выглядеть она будет примерно следующим образом:
```sh
# На Windows пригласительная строка Anaconda Prompt (4.11.0) выглядит так:
(base) C:\Users\IlonMusk>
#   (base) - маркер активного conda enviroment
#   C:\Users\IlonMusk - путь к текущей рабочей директории
#   > - разделитель prompt и области для введения команд справа

# Немного иначе выглядит стандартный prompt командной оболочки в MacOS / Linux:
(base) IlonMusk@TeslaMac ~ %
#   (base) - маркер активного conda enviroment
#   IlonMusk - имя пользователя
#   @ - разделительный символ "at" - тот же смысл что и для e-mail
#   TeslaMac - имя компьютера "на котором" пользователем запущена оболочка
#   ~ - путь к текущей рабочей директории (~ означает домашнюю папку)
#   % - разделитель prompt и области для введения команд справа
```
В приведенных выше примерах закомментированные решеткой строки кратко поясняют из чего состоит так называемый prompt[^9] &ndash; левая части командной строки с информацией командной оболочки. Главной подсказкой готовности конды к работе является маркер активного окружения (имя в скобочках) предваряющий остальную информацию. Как нетрудно догадаться на примерах выше активным является базовое окружение ==base==. Его невозможно удалить и не стоит засорять без необходимости. Для знакомства с функционалом *conda* достаточно ввести в командной строке `conda` и нажать Enter.

[^9]: Prompt &ndash; левая часть командной строки, контролируемая командной оболочкой. Чаще всего предваряет поле для вводимой команды информацией о текущей дериктории и приглашающим символом `>`, `$` или `%`. Prompt может быть настроен через редактирование конфигурационных файлов командной оболочки (например `.bashrc` для *bash* или `.ps1` для *powershell*), чтобы придать терминалу более модный и/или информативный вид (см. например терминалы [r/unixporn/](https://www.reddit.com/r/unixporn/)). Например, помимо текущей дерикотории можно кастомизировать Prompt для вывода информации о пользователе, рабочем окружении (что кстати и делает Anaconda Prompt), состоянии git репозитория и.т.д.

>   :scroll: *Ответом будет краткая справка об основных командах*
>   <details>
>   <summary><i>Подробнее о работе с командной строкой</i></summary>
>
>   - Во-первых убедимся, что после попытки запуска команды в терминале НЕ появилось сообщение[^10] об ошибке красным шрифтом.
>       ```
>       conda : The term 'conda' is not recognized as the name of a cmdlet,
>       function, script file, or operable program. Check the spelling of the
>       name, or if a path was included, verify that the path is correct and
>       try again.
>       ```
>   - Если команда выполнилась как задумано, выводе терминала будет таким
>       ```
>       usage: conda-script.py [-h] [-V] command ...
>       
>       conda is a tool for managing and deploying applications, environments and packages.
>       
>       Options:
>       
>       positional arguments:
>         command
>           clean        Remove unused packages and caches.
>           compare      Compare packages between conda environments.
>           config       Modify configuration values in .condarc. This is modeled
>                        after the git config command. Writes to the user .condarc
>                        file (C:\Users\<IlonMusk>\.condarc) by default.
>           create       Create a new conda environment from a list of specified
>                        packages.
>           help         Displays a list of available conda commands and their help
>                        strings.
>           info         Display information about current conda install.
>           init         Initialize conda for shell interaction. [Experimental]
>           install      Installs a list of packages into a specified conda
>                        environment.
>           list         List linked packages in a conda environment.
>           package      Low-level conda package utility. (EXPERIMENTAL)
>           remove       Remove a list of packages from a specified conda environment.
>           uninstall    Alias for conda remove.
>           run          Run an executable in a conda environment.
>           search       Search for packages and display associated information. The
>                        input is a MatchSpec, a query language for conda packages.
>                        See examples below.
>           update       Updates conda packages to the latest compatible version.
>           upgrade      Alias for conda update.
>
>       optional arguments:
>         -h, --help     Show this help message and exit.
>         -V, --version  Show the conda version number and exit.
>
>       conda commands available from other packages:
>         content-trust
>         env
>       ```
>   - Существует множество инструментов прекрасно работающих в командной строке. Очень часто они использует этот же шаблон:
>       ```
>       <имя программного инструмента> <имя команды> [опции] аргументы
>       ```
>   - Чтобы немного освоится с командованием, введем следующие фразы, завершая каждую из строк Enter.
>       ```sh
>       conda info -h
>       conda info
>       conda list --help
>       conda list
>       ```
>   - Общий совет для работы с любым инструментом в командной строке &ndash; сначала вводить команду без аргументов с короткой опцией `-h` или длинной `--help`. В большинстве толковых консольных программ эта команда выведет документацию и/или подсказку по использованию.

[^10]: Сообщение об ошибке красным шрифтом чаще всего дает подсказку о том, что пошло не так. В приведенном примере, оболочка командной строки не может распознать команду/программу. Предположим имя программы все же написано правильно, например, `conda`. Распространен вариант, когда программа установлена, однако оболочка командной строки просто не в курсе, где она находится &ndash; в переменной окружения PATH не перечислена папка, в которой лежит исполняемый скрипт / .exe файл / symlink к программе. Разбор, что такое переменные окружения и как настроить PATH опять же потребует отдельной лекции о работе с терминалом и командной строкой, которая возможно будет добавлена в будущих итерациях руководства. Пока же предлагается довольствоваться [ссылкой на википедию](https://ru.wikipedia.org/wiki/PATH_(%D0%BF%D0%B5%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D0%BD%D0%B0%D1%8F))

Часто используемые команды:
- Вывести список существующих окружений: `conda env list`
- Вывести список установленных пакетов в активном окружении: `conda list`
- Вывести список пакетов в окружении: `conda list --name <имя_окружения>`
- Обновить пакеты в окружении: `conda update -n <имя_окружения> <имя_пакета>`
- Обовить все пакеты в активном окружении: `conda update -all`

Далее разберем как же создается новое *conda environment* на примере всеобъемлющего рабочего окружения ==seismology==, включающего в себя необходимые инструменты для запуска всех интерактивных тетрадей.

##### :notebook: Рабочее окружение для всего руководства {#env-allinone}

>   :hourglass: *Создание / установка в одну командную строку* :godmode
>   <details>
>   <summary><i>если подробности установки пакетов не интересуют</i></summary>
>
>   ```sh
>   conda create --name=seismology --channel=conda-forge python=3.9 geos=3.9 gmt pygmt cartopy obspy ipykernel
>   ```
>   - Если установлена **Anaconda** достаточно скопировать эту строку и выполнить команду нажав Enter
>   - Если установлена **miniconda**, то не забываем в конце строки через пробел дописать `jupyter notebook`
>   </details>

Разумеется, имя для нового окружения можно выбрать какое душе угодно, суть от этого не меняется. Однако для удобства дальнейших пояснений данный вариант рабочего окружения называется ==seismology== и ссылки в тексте или же примерах командной строки будут привязаны к этому названию по-умолчанию. Решившим назвать окружение как-то пооригинальней необходимо внимательно копировать команды из дальнейших блоков и соответственно заменять имя окружения.
Итак, окружение (*conda environment*) можно создать в одну строку или пошагово. В любом случае начинается этот процесс одной командой, просто в первом случае он ей же и заканчивается :laughing: (см. пример в блоке выше).
Здесь мы разберем этот процесс пошагово, прокомментировав необходимость каждого из основных устанавливаемых пакетов. Вот и первая необходимая команда:

```sh
conda create --name=seismology
```

В таком минималистичном виде команда по сути только создаст папку для будущего окружения и добавит туда парочку необходимых для работы менеджера пакетов файлов. В ходе выполнения команда выведет *Package Plan* (пустой, так как мы никаких пакетов не запросили к установке) и *environment location* (путь к папке) где будет располагатся будущее окружение, после чего запросит разрешение на продолжение. Вводим `y` и нажимаем Enter. Первый шаг сделан. Теперь осталось наполнить окружение пакетами и инструментами.

Для первой интерактивной тетради нам потребуется уже упоминавшийся пакет [ObsPy](https://docs.obspy.org/). Установим его, указав канал *conda* `--channel=conda-forge`:

```sh
conda install --name=seismology --channel=conda-forge obspy
```

>   **ВАЖНО**: Если установлен дистрибутив *miniconda*, то надо не забыть заодно установить в новое окружение *Jupyter Notebook*
>   ```sh
>   conda install --name=seismology jupyter notebook
>   ```

В ходе выполнения команда снова выведет обновленный *Package Plan* (в этот раз  наполненный различными зависимостями), после чего запросит разрешение на продолжение. Вводим `y` и нажимаем Enter. Второй шаг сделан. Теперь осталось подождать пока *conda* сделает свою работу. После скачивания и установки всех пакетов нам остается только проверить, что окружение работоспособно. Активируем окружение командной:

```sh
conda activate seismology
```

Подмечаем, что маркер активного окружения в левой части командной строки изменился с ==base== на ==seismology==. Осталось только проверить, что в данным окружении импорт *ObsPy* не вызовет ошибки. Для этого можно запустить интерактивный сеанс *Python* в консоли или же просто выполнить следующую команду, которая запустит интерпретатор и передаст на вход пару строчек кода для выполнения.

```sh
python -c "import obspy; print(f'ObsPy version: {obspy.__version__}')"
```

Если результат выполнения выглядит так:

```sh
ObsPy version: 1.3.0
```

значит созданное рабочее окружение функционирует и пора запускать *Jupyter Notebook*.


#### :heavy_plus_sign: Добавление окружения в *Jupyter Notebook* {#kernel-add}
Теперь настал важный момент. Мы создали новое рабочее окружение, активировали его в консоли, удостоверились что мы можем без ошибок импортировать необходимые нам пакеты. Казалось бы, осталось только запустить *Jupiter Notebook*...

... и выяснить, что первым делом он обнаруживает только базовое окружении.
Поэтому ещё ненадолго задержимся в консоли.
Нам нужно добавить новое окружение в список вычислительных ядер (*Python Kernels*) исполняемых нашим *Jupiter Notebook*. В первую очередь определяемся в котором из окружений установлен *Jupiter Notebook*. Если установлен дистрибутив *Anaconda*, то выходим обратно в базовое окружение командой ```conda deactivate```, если же установлена *miniconda* и предыдущая секция прочитана внимательно, то остаемся в текущем окружении.

Для добавления нового окружения в список ядер *Jupiter Notebook* в консоли пишем:
```sh
ipython kernel install --user --name=seismology
```

Если *Jupiter Notebook* был уже запущен, то достаточно обновить страницу браузера (F5), в котором запущен *Jupyter*.
Для того чтобы запустить его из командной строки достаточно ввести
```sh
jupyter notebook
```

Выбираем необходимую часть руководства и в верхней части страницы с запущенной тетрадью (тулбар) выбираем *Kernel -> Change kernel -> seismology*


#### :recycle: Удаление рабочего окружения (при необходимости) {#env-reset}

Для удаления рабочего окружения (*conda environment*) необходимо его сначала деактивировать. Затем удалить по имени.
```sh
conda deactivate

conda remove --name seismology --all
```

Не стоит забывать об удалении ядра несуществующего более окружения из списка *Jupyter Notebook*:
```sh
# Вывести список
jupyter kernelspec list
# Удалить ядро неиспользуемого более окружения
jupyter kernelspec remove <kernel_name>
```


### :bookmark: Примечания
