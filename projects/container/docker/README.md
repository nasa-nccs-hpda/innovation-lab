
[centos@ip-172-30-0-148 mmx]$ sudo docker build -t docker-mmx-root-home-centos  -f Dockerfile.root.home-centos .

[centos@ip-172-30-0-148 mmx]$ sudo docker run -t -i docker-mmx-root-home-centos  python /usr/local/mmx/innovation-lab/mmx/innovation-lab/view/tests/MmxRequestCeleryView.py
