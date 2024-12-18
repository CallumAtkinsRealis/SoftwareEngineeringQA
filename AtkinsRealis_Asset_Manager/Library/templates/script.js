        document.addEventListener('DOMContentLoaded', () => {
            const durationElement = document.getElementById('id_duration');
            const dateToGroup = document.getElementById('id_date_to_group');

            function checkDuration(value) {
                dateToGroup.style.display = value === 'MD' ? 'block' : 'none';
            }

            checkDuration(durationElement.value);
            durationElement.addEventListener('change', () => {
                checkDuration(durationElement.value);
            });

            document.getElementById('goBackButton').addEventListener('click', () => {
                window.history.back();
            });
        });