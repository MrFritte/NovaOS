FROM archlinux:latest
RUN pacman -Syu --noconfirm --needed archiso
WORKDIR /workspace
COPY . /workspace
CMD ["./scripts/build-iso.sh"]
