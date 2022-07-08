import termtables as tt

my_tasks = [['Hours', '157h'], ['Minutes', '56m']]

string = tt.to_string(
                my_tasks,
                style=tt.styles.rounded_thick,
                padding=(0, 3),
            )

print(string)