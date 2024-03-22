library(tidyverse)
library(readxl)
library(dplyr)
library(grid)
library(gridExtra)
library(ggplot2)

courses <- read_xlsx("C:/Users/kmconrad3/Box/BBA Data Lab/Kara/Projects/OUD Course List/COURSE_HISTORY.xlsx")
maj <- read_xlsx("C:/Users/kmconrad3/Box/BBA Data Lab/Kara/Projects/OUD Course List/OUD_MASTER_LIST.xlsx")


#:::::::::::::::::::::::::::::Schools:::::::::::::::::::::::::::::
#table(courses$COURSE_ACADEMIC_GROUP, courses$SUBJECT_CODE) #to see school codes
count_school <- courses %>%
  mutate(school_col = case_when(
    SUBJECT_CODE %in% c(231, 232, 233, 234, 235, 236, 237, 238, 239, 241, 242) ~ "BUS", 
    SUBJECT_CODE %in% c(104, 106, 156, 188, 208, 224, 244, 250, 296, 351, 352, 380, 400, 416, 420, 448, 500, 502, 512, 520, 535, 544, 550, 551, 600, 736, 754, 778, 820, 888, 900, 932, 963) ~ "L&S",
    PRIMARY_SUBJECT_CODE == 239 ~ "BUS",
    SUBJECT_CODE == 476 | SUBJECT_CODE == 192 ~ "ALS",
    SUBJECT_CODE == 315 | SUBJECT_CODE == 942 | SUBJECT_CODE == 146 | SUBJECT_CODE == 194 | SUBJECT_CODE == 168 ~ "EDU",
    SUBJECT_CODE == 359 | SUBJECT_CODE == 247 | SUBJECT_CODE == 271 | SUBJECT_CODE == 230 ~ "HEC", 
    SUBJECT_CODE == 360 ~ "IES",
    SUBJECT_CODE == 692 ~ "NUR",
    SUBJECT_CODE == 452 ~ "MED", TRUE ~ "OTHER"))

count_school2 <- count_school %>%
  mutate(count=1) %>%
  group_by(CAMPUS_ID, school_col) %>%
  summarize(school_count = sum(count), credit_count=sum(CREDITS_TAKEN))%>%
  group_by(school_col) %>%
  summarize(avg = round(mean(school_count, na.rm = TRUE), digits=2), 
            school_count = sum(school_count, na.rm = TRUE),
            avg_cred = round(mean(credit_count), digits=2),
            credit_count = sum(credit_count))
count_school2 <- count_school2[order(count_school2$school_count, decreasing=TRUE),]

colnames(count_school2) <- c("Schools","Avg courses taken", "Total seats", "Avg credits", "Total credits")
tt <- ttheme_default(colhead=list(fg_params = list(parse=TRUE)))
grid.table(count_school2, theme=tt)


##:::::::::::::::::::::::::::::Class subjects:::::::::::::::::::::::::::::
count_bba_subject <- count_school %>%
  filter(school_col == "BUS") %>%
  mutate(count = 1) %>%
  group_by(CAMPUS_ID, SUBJECT_DESCR) %>%
  summarize(
    subject_count = sum(count), credit_count=sum(CREDITS_TAKEN))%>%
  group_by(SUBJECT_DESCR) %>%
  summarize(avg = round(mean(subject_count, na.rm = TRUE), digits=2), 
            subject_count = sum(subject_count, na.rm = TRUE),
            avg_cred = round(mean(credit_count), digits=2),
            credit_count = sum(credit_count))
count_bba_subject <- count_bba_subject[order(count_bba_subject$subject_count, decreasing=TRUE),]

colnames(count_bba_subject) <- c("Subjects","Avg courses taken", "Total seats", "Avg credits", "Total credits")
tt <- ttheme_default(colhead=list(fg_params = list(parse=TRUE)))
grid.table(count_bba_subject, theme=tt)


count_subject <- count_school %>%
  filter(school_col != "BUS") %>%
  mutate(count = 1) %>%
  group_by(CAMPUS_ID, SUBJECT_DESCR) %>%
  summarize(
    subject_count = sum(count), credit_count=sum(CREDITS_TAKEN))%>%
  group_by(SUBJECT_DESCR) %>%
  summarize(avg = round(mean(subject_count, na.rm = TRUE), digits=2), 
            subject_count = sum(subject_count, na.rm = TRUE),
            avg_cred = round(mean(credit_count), digits=2),
            credit_count = sum(credit_count))
count_subject <- head( count_subject[order(count_subject$subject_count, decreasing=TRUE),], 15 )

colnames(count_subject) <- c("Subjects","Avg courses taken", "Total seats", "Avg credits", "Total credits")
tt <- ttheme_default(colhead=list(fg_params = list(parse=TRUE)))
grid.table(count_subject, theme=tt)


#:::::::::::::::::::::::::::::Classes:::::::::::::::::::::::::::::
ppl <- length(unique(maj$CAMPUS_ID))
count_bba_course <- count_school %>%
  filter(school_col == "BUS") %>%
  mutate(count=1)%>%
  group_by(CAMPUS_ID, COURSE_TITLE) %>%
  summarize(course_count = sum(count))%>%
  group_by(COURSE_TITLE)%>%
  summarize(perc = round((sum(course_count, na.rm = TRUE)/ppl)*100, digits=2),
            course_count = sum(course_count, na.rm = TRUE))
count_bba_course <- head( count_bba_course[order(count_bba_course$course_count, decreasing=TRUE),], 10)

colnames(count_bba_course) <- c("Courses","Percent who've taken", "Total seats")
tt <- ttheme_default(colhead=list(fg_params = list(parse=TRUE)))
grid.table(count_bba_course, theme=tt)


count_course <- count_school %>%
  filter(school_col != "BUS") %>%
  mutate(count=1)%>%
  group_by(CAMPUS_ID, COURSE_TITLE) %>%
  summarize(course_count = sum(count))%>%
  group_by(COURSE_TITLE)%>%
  summarize(perc = round((sum(course_count, na.rm = TRUE)/ppl)*100, digits=2),
            course_count = sum(course_count, na.rm = TRUE))
count_course <- head(count_course[order(count_course$course_count, decreasing=TRUE),], 10)

colnames(count_course) <- c("Courses","Percent who've taken", "Total seats")
tt <- ttheme_default(colhead=list(fg_params = list(parse=TRUE)))
grid.table(count_course, theme=tt)


#:::::::::::::::::::::::::::::By cohort:::::::::::::::::::::::::::::
#df <- merge(courses, maj[, c("CAMPUS_ID", "TERM", "ACAD_PLAN_DESCR")], by.y="CAMPUS_ID")
df <- left_join(maj, courses, by = c("CAMPUS_ID"))

df <- df %>%
  mutate(TERM = case_when(TERM %in% c(1226, 1232, 1234) ~ "Coh 2",
                          TERM == 1222 | TERM == 1224 ~ "Coh 1",
                          TERM == 1236 | TERM == 1242 ~ "Coh 3", TRUE ~ "X"))

df$enrollment = 1

df <- df %>%
  group_by(CAMPUS_ID, TERM, SUBJECT_DESCR) %>%
  summarise(
    enrollment = sum(enrollment))

df <- df %>%
  mutate(unique_enrollment = case_when(enrollment >= 1 ~ 1, TRUE ~ 0))

cohort_sub <- df %>%
  group_by(TERM, SUBJECT_DESCR) %>%
  summarise(enrollment = sum(unique_enrollment))

cohort_count <- df %>%
  group_by(TERM) %>%
  mutate(unique_count = n_distinct(CAMPUS_ID)) %>%
  summarize(unique_count = max(unique_count))

cohort_data <- left_join(cohort_sub, cohort_count ,by =c("TERM"))


#Plot of unique students taking a course by subject, by cohort
cohort_data %>%
  ggplot(aes(x=TERM, y = enrollment, fill = as.factor(SUBJECT_DESCR))) + 
  geom_col(position = 'dodge')
