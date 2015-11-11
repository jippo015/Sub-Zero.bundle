# coding=utf-8

import logging
from subliminal.video import Episode, Movie

logger = logging.getLogger(__name__)


def compute_score(matches, video, scores=None):
    """Compute the score of the `matches` against the `video`.
    Some matches count as much as a combination of others in order to level the final score:
      * `hash` removes everything else
      * For :class:`~subliminal.video.Episode`
        * `imdb_id` removes `series`, `tvdb_id`, `season`, `episode`, `title` and `year`
        * `tvdb_id` removes `series` and `year`
        * `title` removes `season` and `episode`
    :param video: the video to get the score with.
    :type video: :class:`~subliminal.video.Video`
    :param dict scores: scores to use, if `None`, the :attr:`~subliminal.video.Video.scores` from the video are used.
    :return: score of the subtitle.
    :rtype: int

    # patch: remove score cap for enabling individual boost
    """
    final_matches = matches.copy()
    scores = scores or video.scores

    logger.info('Computing score for matches %r and %r', matches, video)

    is_episode = isinstance(video, Episode)

    # remove equivalent match combinations
    if 'hash' in final_matches:
        if is_episode:
            # we're an episode and we have "hash" set.
            if {"season", "episode"} <= set(final_matches):
                # season and episode matched, hash is valid
                logger.info('Using valid hash, as season/episode are correct (%r) and (%r)', matches, video)
                final_matches &= {'hash', 'hearing_impaired'}
            else:
                # season and episode didn't match, invalidate hash
                logger.info('Ignoring hash as season/episode are wrong (%r) and (%r)', matches, video)
                final_matches -= {"hash"}
        else:
            # hash trumps everything on non-episode videos
            final_matches &= {'hash', 'hearing_impaired'}

    elif is_episode:
        if 'imdb_id' in final_matches:
            final_matches -= {'series', 'tvdb_id', 'season', 'episode', 'title', 'year'}
        if 'tvdb_id' in final_matches:
            final_matches -= {'series', 'year'}
        if 'title' in final_matches:
            final_matches -= {'season', 'episode'}

    # compute score
    logger.debug('Final matches: %r', final_matches)
    score = sum((scores[match] for match in final_matches))
    logger.info('Computed score %d', score)

    return score