# Copyright (C) 2022 Robin Jespersen
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

FROM python:3.7-stretch

RUN mkdir -p /app
COPY ./app /app
COPY ./requirements.txt /app/requirements.txt

RUN chmod +x /app/main.py
RUN chmod +x /app/healthcheck.py

WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

HEALTHCHECK --interval=1m --timeout=10s --start-period=10s CMD /app/healthcheck.py

CMD ["python","-u","/app/main.py"]
